import pytest
from sqlmodel import select

from dundie.core import transfer
from dundie.database import get_session
from dundie.models import Movement, Person
from dundie.utils.db import add_person


@pytest.mark.unit
def test_transfer_points_success():
    """Testa transferência de pontos com sucesso"""
    from_email = "test_transfer_from@dundie.com"
    to_email = "test_transfer_to@dundie.com"

    with get_session() as session:
        # Limpa dados anteriores
        for email in [from_email, to_email]:
            person = session.exec(select(Person).where(Person.email == email)).first()
            if person:
                if person.balance:
                    session.delete(person.balance)
                if person.user:
                    session.delete(person.user)
                movements = session.exec(select(Movement).where(Movement.person_id == person.id)).all()
                for mov in movements:
                    session.delete(mov)
                session.delete(person)
        session.commit()

        # Cria pessoas
        # Pessoa que vai transferir (Manager - começa com 100)
        from_person = Person(
            name="Transfer From",
            dept="Management",
            role="Manager",
            email=from_email,
            currency="USD",
        )
        from_person, created = add_person(session, from_person)
        assert created is True

        # Pessoa que vai receber (Salesman - começa com 500)
        to_person = Person(
            name="Transfer To",
            dept="Sales",
            role="Salesman",
            email=to_email,
            currency="USD",
        )
        to_person, created = add_person(session, to_person)
        assert created is True

        session.commit()

    # Realiza transferência
    result = transfer(from_email, to_email, 50)

    # Verifica resultado
    assert result["success"] is True
    assert result["from_balance"] == 50  # 100 - 50
    assert result["to_balance"] == 550  # 500 + 50


@pytest.mark.unit
def test_transfer_points_insufficient_balance():
    """Testa transferência com saldo insuficiente"""
    from_email = "test_transfer_insuf_from@dundie.com"
    to_email = "test_transfer_insuf_to@dundie.com"

    with get_session() as session:
        # Limpa dados anteriores
        for email in [from_email, to_email]:
            person = session.exec(select(Person).where(Person.email == email)).first()
            if person:
                if person.balance:
                    session.delete(person.balance)
                if person.user:
                    session.delete(person.user)
                movements = session.exec(select(Movement).where(Movement.person_id == person.id)).all()
                for mov in movements:
                    session.delete(mov)
                session.delete(person)
        session.commit()

        # Cria pessoas
        from_person = Person(
            name="Insuf From",
            dept="Management",
            role="Manager",
            email=from_email,
            currency="USD",
        )
        from_person, created = add_person(session, from_person)
        assert created is True

        to_person = Person(
            name="Insuf To",
            dept="Sales",
            role="Salesman",
            email=to_email,
            currency="USD",
        )
        to_person, created = add_person(session, to_person)
        assert created is True

        session.commit()

    # Tenta transferir mais do que tem (Manager tem 100)
    result = transfer(from_email, to_email, 200)

    assert result["success"] is False
    assert "Insufficient balance" in result["error"]


@pytest.mark.unit
def test_transfer_points_negative_value():
    """Testa transferência com valor negativo"""
    from dundie.core import transfer

    result = transfer("from@test.com", "to@test.com", -50)

    assert result["success"] is False
    assert "Value must be positive" in result["error"]


@pytest.mark.unit
def test_transfer_points_sender_not_found():
    """Testa transferência com remetente inexistente"""
    from dundie.core import transfer

    result = transfer("nonexistent@dundie.com", "to@dundie.com", 50)

    assert result["success"] is False
    assert "Sender not found" in result["error"]


@pytest.mark.unit
def test_transfer_points_recipient_not_found():
    """Testa transferência com destinatário inexistente"""
    from dundie.core import transfer

    unique_email = "test_sender_exists@dundie.com"

    # Limpa dados anteriores
    with get_session() as session:
        person = session.exec(select(Person).where(Person.email == unique_email)).first()
        if person:
            if person.balance:
                session.delete(person.balance)
            if person.user:
                session.delete(person.user)
            session.delete(person)
        session.commit()

    # Cria remetente
    with get_session() as session:
        person = Person(
            name="Sender Exists",
            dept="Management",
            role="Manager",
            email=unique_email,
            currency="USD",
        )
        person, created = add_person(session, person)
        assert created is True
        session.commit()

    result = transfer(unique_email, "nonexistent@dundie.com", 50)

    assert result["success"] is False
    assert "Recipient not found" in result["error"]

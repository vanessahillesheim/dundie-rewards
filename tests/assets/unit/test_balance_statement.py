import pytest
from sqlmodel import select

from dundie.core import get_balance, get_statement, add
from dundie.database import get_session
from dundie.models import Movement, Person
from dundie.utils.db import add_person


@pytest.mark.unit
def test_get_balance_success():
    """Testa obtenção de saldo com sucesso"""
    unique_email = "test_balance_success@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.balance:
                session.delete(person.balance)
            if person.user:
                session.delete(person.user)
            movements = session.exec(
                select(Movement).where(Movement.person_id == person.id)
            ).all()
            for mov in movements:
                session.delete(mov)
            session.delete(person)
        session.commit()
    
    # Cria pessoa
    with get_session() as session:
        person = Person(
            name="Balance Test",
            dept="Sales",
            role="Salesman",
            email=unique_email,
            currency="USD"
        )
        person, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Obtém saldo
    result = get_balance(unique_email)
    
    assert result is not None
    assert result["name"] == "Balance Test"
    assert result["balance"] == 500  # Salesman começa com 500
    assert result["currency"] == "USD"


@pytest.mark.unit
def test_get_balance_user_not_found():
    """Testa obtenção de saldo para usuário inexistente"""
    result = get_balance("nonexistent@dundie.com")
    assert result is None


@pytest.mark.unit
def test_get_statement_success():
    """Testa obtenção de extrato com sucesso"""
    unique_email = "test_statement_success@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.balance:
                session.delete(person.balance)
            if person.user:
                session.delete(person.user)
            movements = session.exec(
                select(Movement).where(Movement.person_id == person.id)
            ).all()
            for mov in movements:
                session.delete(mov)
            session.delete(person)
        session.commit()
    
    # Cria pessoa e faz movimentações
    with get_session() as session:
        person = Person(
            name="Statement Test",
            dept="Sales",
            role="Salesman",
            email=unique_email,
            currency="USD"
        )
        person, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Adiciona algumas movimentações
    add(100, email=unique_email)
    add(50, email=unique_email)
    add(-30, email=unique_email)
    
    # Obtém extrato
    movements = get_statement(unique_email, limit=3)
    
    assert len(movements) == 3
    for mov in movements:
        assert "date" in mov
        assert "value" in mov
        assert "actor" in mov


@pytest.mark.unit
def test_get_statement_with_limit():
    """Testa obtenção de extrato com limite"""
    unique_email = "test_statement_limit@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.balance:
                session.delete(person.balance)
            if person.user:
                session.delete(person.user)
            movements = session.exec(
                select(Movement).where(Movement.person_id == person.id)
            ).all()
            for mov in movements:
                session.delete(mov)
            session.delete(person)
        session.commit()
    
    # Cria pessoa
    with get_session() as session:
        person = Person(
            name="Statement Limit Test",
            dept="Sales",
            role="Salesman",
            email=unique_email,
            currency="USD"
        )
        person, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Adiciona várias movimentações
    for i in range(5):
        add(10, email=unique_email)
    
    # Obtém extrato com limite de 3
    movements = get_statement(unique_email, limit=3)
    
    assert len(movements) == 3


@pytest.mark.unit
def test_get_statement_user_not_found():
    """Testa obtenção de extrato para usuário inexistente"""
    movements = get_statement("nonexistent@dundie.com")
    assert movements == []
import pytest
from sqlmodel import select

from dundie.core import read
from dundie.database import get_session
from dundie.models import Movement, Person
from dundie.utils.db import add_person


@pytest.mark.unit
def test_read_with_query():
    # PRIMEIRO: Limpa dados problemáticos de testes anteriores
    problematic_emails = [
        "test_commit_joe@doe.com",
        "1testejoe@doe.com",
        "jim@dundermifflin.com",
        "schrute@dundermifflin.com",
        "glewis@dundermifflin.com",
    ]

    with get_session() as session:
        for email in problematic_emails:
            person = session.exec(
                select(Person).where(Person.email == email)
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

    # AGORA: Teste normal com emails únicos
    with get_session() as session:
        # Adiciona Joe Doe
        joe_data = {
            "name": "Joe Doe",
            "dept": "Sales",
            "role": "Salesman",
            "email": "test_read_joe@doe.com",
            "currency": "USD",
        }
        joe_person = Person(**joe_data)
        _, created = add_person(session, joe_person)
        assert created is True

        # Adiciona Jim Doe
        jim_data = {
            "name": "Jim Doe",
            "dept": "Management",
            "role": "Manager",
            "email": "test_read_jim@doe.com",
            "currency": "USD",
        }
        jim_person = Person(**jim_data)
        _, created = add_person(session, jim_person)
        assert created is True

        session.commit()

    response = read()
    assert len(response) == 2

    response = read(dept="Management")
    assert len(response) == 1
    assert response[0]["name"] == "Jim Doe"

    response = read(email="test_read_joe@doe.com")
    assert len(response) == 1
    assert response[0]["name"] == "Joe Doe"

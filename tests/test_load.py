"""Core = testano o corpo de dindie"""

import pytest
from sqlmodel import select

from dundie.core import load
from dundie.database import get_session
from dundie.models import Person, Balance, Movement

from .constants import PEOPLE_FILE


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_has_3_people():
    """Testando a função load"""
    # Limpa dados antes do teste
    with get_session() as session:
        all_people = session.exec(select(Person)).all()
        for person in all_people:
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
    
    assert len(load(PEOPLE_FILE)) == 3


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_first_name_starts_with_j():
    """Testando o nome da primeira pessoa"""
    # Limpa dados antes do teste
    with get_session() as session:
        all_people = session.exec(select(Person)).all()
        for person in all_people:
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
    
    assert load(PEOPLE_FILE)[0]["name"] == "Jim Halpert"
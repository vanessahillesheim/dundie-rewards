import os

import pytest
from click.testing import CliRunner
from sqlmodel import select

from dundie.cli import main
from dundie.database import get_session
from dundie.models import Balance, Movement, Person, User
from dundie.utils.db import add_person, set_initial_balance
from dundie.utils.user import get_password_hash

cmd = CliRunner()


@pytest.fixture
def authenticated_user():
    """Cria um usuário autenticado para os testes"""
    email = "test_cli_user@dundie.com"

    with get_session() as session:
        # Limpa dados anteriores
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

        # Cria pessoa
        person = Person(
            name="Test User",
            dept="Management",
            role="Manager",
            email=email,
            currency="USD",
        )
        person, created = add_person(session, person)
        assert created is True
        session.commit()

    # Define senha
    from dundie.utils.user import set_password

    set_password(email, "test123")

    # Salva credenciais no ambiente para o CLI
    os.environ["DUNDIE_USER"] = email
    os.environ["DUNDIE_PASSWORD"] = "test123"

    return email


@pytest.mark.integration
def test_show_command(authenticated_user):
    """Testa comando show (antigo balance)"""
    # CORRIGIDO: usa "show" em vez de "balance"
    result = cmd.invoke(main, ["show"])

    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Relatório de Pontos" in result.output


@pytest.mark.integration
def test_show_command_for_other_user(authenticated_user):
    """Testa comando show para outro usuário"""
    # Cria outro usuário
    other_email = "other_user@dundie.com"
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(select(Person).where(Person.email == other_email)).first()
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

        # Cria pessoa
        person = Person(
            name="Other User",
            dept="Sales",
            role="Salesman",
            email=other_email,
            currency="USD",
        )
        person, created = add_person(session, person)
        session.commit()

    # CORRIGIDO: usa "show" em vez de "balance"
    result = cmd.invoke(main, ["show", "--email", other_email])
    assert result.exit_code == 0
    assert "Other User" in result.output


@pytest.mark.integration
def test_statement_command(authenticated_user):
    """Testa comando statement"""
    # CORRIGIDO: adiciona --email para não pedir interativamente
    result = cmd.invoke(main, ["statement", "--email", authenticated_user])

    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Extrato" in result.output


@pytest.mark.integration
def test_statement_command_with_limit(authenticated_user):
    """Testa comando statement com limite"""
    # CORRIGIDO: adiciona --email para não pedir interativamente
    result = cmd.invoke(main, ["statement", "--email", authenticated_user, "--limit", "5"])

    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Extrato" in result.output

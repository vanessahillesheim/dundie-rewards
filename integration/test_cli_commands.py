import os
import pytest
from click.testing import CliRunner
from sqlmodel import select

from dundie.cli import main
from dundie.database import get_session
from dundie.models import Person, User, Balance, Movement
from dundie.utils.user import get_password_hash
from dundie.utils.db import add_person, set_initial_balance

cmd = CliRunner()


@pytest.fixture
def authenticated_user():
    """Cria um usuário autenticado para testes de integração"""
    unique_email = "test_cli_user@dundie.com"

    # Limpa dados anteriores
    with get_session() as session:
        # Remove todas as movimentações e balances primeiro
        person = session.exec(select(Person).where(Person.email == unique_email)).first()
        if person:
            # Remove movimentações
            movements = session.exec(select(Movement).where(Movement.person_id == person.id)).all()
            for mov in movements:
                session.delete(mov)
            # Remove balance
            if person.balance:
                session.delete(person.balance)
            # Remove user
            if person.user:
                session.delete(person.user)
            # Remove person
            session.delete(person)
        session.commit()

    # Cria usuário
    with get_session() as session:
        person = Person(
            name="CLI Test User",
            dept="Management",
            role="Manager",
            email=unique_email,
            currency="USD",
        )
        session.add(person)
        session.flush()

        # Cria usuário com senha
        user = User(person_id=person.id, password=get_password_hash("test123"))
        session.add(user)
        session.flush()

        # Inicializa balance
        set_initial_balance(session, person)

        session.commit()

        # Força carregamento dos relacionamentos dentro da sessão
        session.refresh(person)
        session.refresh(user)

    # Configura variáveis de ambiente para autenticação
    os.environ["DUNDIE_USER"] = unique_email
    os.environ["DUNDIE_PASSWORD"] = "test123"

    yield unique_email

    # Limpa após teste
    if "DUNDIE_USER" in os.environ:
        del os.environ["DUNDIE_USER"]
    if "DUNDIE_PASSWORD" in os.environ:
        del os.environ["DUNDIE_PASSWORD"]


@pytest.mark.integration
def test_balance_command(authenticated_user):
    """Testa comando balance"""
    result = cmd.invoke(main, ["balance"])

    # Debug se necessário
    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Balance Report" in result.output
    assert authenticated_user in result.output


@pytest.mark.integration
def test_balance_command_for_other_user(authenticated_user):
    """Testa comando balance para outro usuário"""
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

    result = cmd.invoke(main, ["balance", "--email", other_email])
    assert result.exit_code == 0
    assert "Balance Report" in result.output
    assert other_email in result.output


@pytest.mark.integration
def test_statement_command(authenticated_user):
    """Testa comando statement"""
    result = cmd.invoke(main, ["statement"])

    # Debug se necessário
    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Statement" in result.output


@pytest.mark.integration
def test_statement_command_with_limit(authenticated_user):
    """Testa comando statement com limite"""
    result = cmd.invoke(main, ["statement", "--limit", "5"])

    # Debug se necessário
    if result.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {result.exit_code}")
        print(f"[DEBUG] Output: {result.output[:500]}")

    assert result.exit_code == 0
    assert "Statement" in result.output

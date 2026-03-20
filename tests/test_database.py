import pytest
from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person, Balance, Movement, User, InvalidEmailError
from dundie.utils.db import add_person, add_movement
from dundie.utils.email import check_valid_email


@pytest.mark.unit
def test_database_schema():
    """Testa se o banco de dados tem as tabelas corretas"""
    with get_session() as session:
        # Verifica se as tabelas existem executando queries simples
        people = session.exec(select(Person)).all()
        balances = session.exec(select(Balance)).all()
        movements = session.exec(select(Movement)).all()
        users = session.exec(select(User)).all()
        
        # Todos devem ser listas (podem estar vazias)
        assert isinstance(people, list)
        assert isinstance(balances, list)
        assert isinstance(movements, list)
        assert isinstance(users, list)


@pytest.mark.unit
def test_commit_to_database():
    """Testa se os dados são persistidos no banco"""
    unique_email = "test_commit_joe@doe.com"
    
    # Limpa dados anteriores
    with get_session() as session:
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
    
    # Adiciona nova pessoa
    with get_session() as session:
        data = {
            "name": "Joe Doe",
            "role": "Salesman",
            "dept": "Sales",
            "email": unique_email,
            "currency": "USD"
        }
        person = Person(**data)
        _, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Verifica se os dados foram salvos
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        assert person is not None
        assert person.name == "Joe Doe"
        assert person.role == "Salesman"
        assert person.dept == "Sales"


@pytest.mark.unit
def test_add_person_for_the_first_time():
    """Testa adicionar pessoa pela primeira vez"""
    unique_email = "1testejoe@doe.com"
    
    # Limpa dados anteriores
    with get_session() as session:
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
    
    # Adiciona pessoa
    with get_session() as session:
        data = {
            "name": "Joe Doe",
            "role": "Salesman",
            "dept": "Sales",
            "email": unique_email,
            "currency": "USD"
        }
        person = Person(**data)
        _, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Verifica se foi criado corretamente
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        assert person is not None
        assert person.name == "Joe Doe"
        assert person.role == "Salesman"
        assert person.dept == "Sales"
        
        # Verifica balance inicial (Salesman começa com 500)
        assert person.balance is not None
        assert person.balance.value == 500
        
        # Verifica se há movimento registrado
        movements = session.exec(
            select(Movement).where(Movement.person_id == person.id)
        ).all()
        assert len(movements) > 0
        assert movements[0].value == 500


@pytest.mark.unit
def test_negative_add_person_invalid_email():
    """Testa adicionar pessoa com email inválido"""
    # Verifica se a função check_valid_email funciona
    assert check_valid_email(".@bla") is False
    
    with get_session() as session:
        data = {
            "name": "Joe Doe",
            "role": "Salesman",
            "dept": "Sales",
            "email": ".@bla",  # Email inválido
            "currency": "USD"
        }
        
        # Cria a pessoa (pode não lançar exceção na criação)
        person = Person(**data)
        
        # Força a validação manualmente chamando o validator
        with pytest.raises(InvalidEmailError):
            # Tenta validar o email manualmente
            Person.validate_email(person.email)


@pytest.mark.unit
def test_add_or_remove_points_for_person():
    """Testa movimentação de pontos em pessoa existente"""
    unique_email = "movement_test_unique@doe.com"
    
    # Limpa dados anteriores
    with get_session() as session:
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
    
    # PASSO 1: Setup - criar pessoa com saldo conhecido
    with get_session() as session:
        data = {
            "name": "Joe Doe",
            "role": "Salesman",
            "dept": "Sales",
            "email": unique_email,
            "currency": "USD"
        }
        person = Person(**data)
        _, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # PASSO 2: Testa remoção de pontos
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        initial_balance = person.balance.value  # Deve ser 500
        
        # Remove 100 pontos
        add_movement(session, person, -100, "manager")
        session.commit()
    
    # PASSO 3: Verifica
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        final_balance = person.balance.value
        
        # Assert principal
        assert final_balance == initial_balance - 100
        
        # Asserts específicos
        if initial_balance == 500:
            assert final_balance == 400
        
        # Verifica se movimento foi registrado
        movements = session.exec(
            select(Movement).where(Movement.person_id == person.id)
        ).all()
        last_movement = movements[-1]
        assert last_movement.value == -100
        assert last_movement.actor == "manager"
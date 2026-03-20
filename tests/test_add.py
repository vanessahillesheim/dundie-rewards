import pytest
from sqlmodel import select

from dundie.core import add, read
from dundie.database import get_session
from dundie.models import Person, Balance, Movement
from dundie.utils.db import add_person, add_movement


@pytest.mark.unit
def test_add_movement():
    """Testa adição de movimentações de pontos"""
    
    # Limpa dados problemáticos de testes anteriores
    problematic_emails = [
        "test_commit_joe@doe.com",      # De test_commit_to_database
        "1testejoe@doe.com",            # De test_add_person_for_the_first_time
        "jim@dundermifflin.com",        # De test_load.py
        "schrute@dundermifflin.com",    # De test_load.py
        "glewis@dundermifflin.com",     # De test_load.py
        "test_read_joe@doe.com",        # Email do teste atual
        "test_read_jim@doe.com",        # Email do teste atual
    ]
    
    with get_session() as session:
        # Remove pessoas problemáticas e seus relacionamentos
        for email in problematic_emails:
            person = session.exec(
                select(Person).where(Person.email == email)
            ).first()
            if person:
                # Remove movimentações
                movements = session.exec(
                    select(Movement).where(Movement.person_id == person.id)
                ).all()
                for mov in movements:
                    session.delete(mov)
                
                # Remove balance
                if person.balance:
                    session.delete(person.balance)
                
                # Remove user se existir
                if person.user:
                    session.delete(person.user)
                
                # Remove pessoa
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
            "currency": "USD"
        }
        joe_person = Person(**joe_data)
        person_joe, created_joe = add_person(session, joe_person)
        assert created_joe is True
        
        # Adiciona Jim Doe
        jim_data = {
            "name": "Jim Doe",
            "dept": "Management",
            "role": "Manager",
            "email": "test_read_jim@doe.com",
            "currency": "USD"
        }
        jim_person = Person(**jim_data)
        person_jim, created_jim = add_person(session, jim_person)
        assert created_jim is True
        
        session.commit()
    
    # Aplica movimentações
    # Joe perde 30 pontos (de 100 de Salesman? ou 500? depende da regra)
    # De acordo com o set_initial_balance, Manager começa com 100, outros com 500
    # Joe é Salesman, começa com 500
    add(-30, email="test_read_joe@doe.com")
    # Todos do departamento Management ganham 90 pontos
    # Jim é Manager, começa com 100
    add(90, dept="Management")
    
    # Verifica os resultados
    with get_session() as session:
        # Recupera os balances atualizados
        joe_person = session.exec(
            select(Person).where(Person.email == "test_read_joe@doe.com")
        ).first()
        jim_person = session.exec(
            select(Person).where(Person.email == "test_read_jim@doe.com")
        ).first()
        
        # Recarrega os balances
        if joe_person.balance:
            session.refresh(joe_person.balance)
        if jim_person.balance:
            session.refresh(jim_person.balance)
        
        # Verifica os valores
        # Joe: Salesman começa com 500 - 30 = 470
        assert joe_person.balance.value == 470
        # Jim: Manager começa com 100 + 90 = 190
        assert jim_person.balance.value == 190


@pytest.mark.unit
def test_add_movement_multiple_people():
    """Testa adição de movimentações para múltiplas pessoas"""
    
    with get_session() as session:
        # Limpa dados de teste anteriores
        test_emails = ["test_multi_joe@doe.com", "test_multi_jane@doe.com"]
        for email in test_emails:
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
        
        # Adiciona pessoas de teste
        people_data = [
            {"name": "Joe Multi", "dept": "Sales", "role": "Salesman", 
             "email": "test_multi_joe@doe.com", "currency": "USD"},
            {"name": "Jane Multi", "dept": "Sales", "role": "Saleswoman", 
             "email": "test_multi_jane@doe.com", "currency": "USD"}
        ]
        
        people = []
        for data in people_data:
            person = Person(**data)
            person, _ = add_person(session, person)
            people.append(person)
        
        session.commit()
    
    # Adiciona pontos para todo o departamento Sales
    add(100, dept="Sales")
    
    # Verifica
    with get_session() as session:
        for email in ["test_multi_joe@doe.com", "test_multi_jane@doe.com"]:
            person = session.exec(
                select(Person).where(Person.email == email)
            ).first()
            if person.balance:
                session.refresh(person.balance)
            # Salesman começa com 500 + 100 = 600 pontos
            assert person.balance.value == 600


@pytest.mark.unit
def test_add_movement_invalid_email():
    """Testa adição de movimentação para email inválido"""
    with pytest.raises(RuntimeError, match="not found"):
        add(50, email="email_inexistente@exemplo.com")


@pytest.mark.unit
def test_add_movement_invalid_dept():
    """Testa adição de movimentação para departamento inválido"""
    with pytest.raises(RuntimeError, match="not found"):
        add(50, dept="Departamento_Inexistente")


@pytest.mark.unit
def test_add_movement_negative_value():
    """Testa adição de valor negativo (perda de pontos)"""
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == "test_negative@doe.com")
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
        person_data = {
            "name": "Test Negative",
            "dept": "Sales",
            "role": "Salesman",
            "email": "test_negative@doe.com",
            "currency": "USD"
        }
        person = Person(**person_data)
        person, created = add_person(session, person)
        assert created is True
        session.commit()
    
    # Aplica perda de pontos
    add(-50, email="test_negative@doe.com")
    
    # Verifica
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == "test_negative@doe.com")
        ).first()
        if person.balance:
            session.refresh(person.balance)
        # Salesman começa com 500 - 50 = 450
        assert person.balance.value == 450
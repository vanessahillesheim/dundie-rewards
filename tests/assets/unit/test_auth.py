import pytest
from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person, User
from dundie.utils.user import get_password_hash


@pytest.mark.unit
def test_authenticate_success():
    """Testa autenticação com sucesso"""
    from dundie.utils.auth import authenticate
    
    unique_email = "test_auth_success@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.user:
                session.delete(person.user)
            session.delete(person)
        session.commit()
        
        # Cria usuário de teste
        person = Person(
            name="Auth Test",
            dept="IT",
            role="Admin",
            email=unique_email,
            currency="USD"
        )
        session.add(person)
        session.flush()
        
        user = User(
            person_id=person.id,
            password=get_password_hash("correct_password")
        )
        session.add(user)
        session.commit()
    
    # Testa autenticação
    result = authenticate(unique_email, "correct_password")
    assert result is True


@pytest.mark.unit
def test_authenticate_wrong_password():
    """Testa autenticação com senha errada"""
    from dundie.utils.auth import authenticate
    
    unique_email = "test_auth_wrong@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.user:
                session.delete(person.user)
            session.delete(person)
        session.commit()
        
        # Cria usuário de teste
        person = Person(
            name="Auth Test",
            dept="IT",
            role="Admin",
            email=unique_email,
            currency="USD"
        )
        session.add(person)
        session.flush()
        
        user = User(
            person_id=person.id,
            password=get_password_hash("correct_password")
        )
        session.add(user)
        session.commit()
    
    # Testa com senha errada
    result = authenticate(unique_email, "wrong_password")
    assert result is False


@pytest.mark.unit
def test_authenticate_user_not_found():
    """Testa autenticação com usuário inexistente"""
    from dundie.utils.auth import authenticate
    
    result = authenticate("nonexistent@dundie.com", "any_password")
    assert result is False


@pytest.mark.unit
def test_get_current_user():
    """Testa busca de usuário atual"""
    from dundie.utils.auth import get_current_user
    
    unique_email = "test_get_user@dundie.com"
    
    with get_session() as session:
        # Limpa dados anteriores
        person = session.exec(
            select(Person).where(Person.email == unique_email)
        ).first()
        if person:
            if person.user:
                session.delete(person.user)
            session.delete(person)
        session.commit()
        
        # Cria usuário de teste
        person = Person(
            name="Get User Test",
            dept="IT",
            role="Admin",
            email=unique_email,
            currency="USD"
        )
        session.add(person)
        session.flush()
        
        user = User(
            person_id=person.id,
            password=get_password_hash("test123")
        )
        session.add(user)
        session.commit()
    
    # Busca usuário - retorna um objeto Person (não um dicionário)
    result = get_current_user(unique_email)
    assert result is not None
    # CORREÇÃO: acessar como atributo, não como dicionário
    assert result.email == unique_email
    assert result.name == "Get User Test"
    assert result.role == "Admin"


@pytest.mark.unit
def test_get_current_user_not_found():
    """Testa busca de usuário inexistente"""
    from dundie.utils.auth import get_current_user
    
    result = get_current_user("nonexistent@dundie.com")
    assert result is None
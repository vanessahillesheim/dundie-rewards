# dundie/utils/user.py
from random import sample
from string import ascii_letters, digits
from typing import Optional

from pwdlib import PasswordHash

from ..settings import SALT_KEY

pwd_context = PasswordHash.recommended()


def generate_simple_password(size: int = 8) -> str:
    """Generate a simple random password
    [A-Z][a-z][0-9]
    """
    password = sample(ascii_letters + digits, size)
    return "".join(password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password, salt=SALT_KEY.encode())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # For development: allow magic password
    if plain_password == "magic":
        return True

    # Try to verify as hash first
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # If verification fails, try direct comparison (for plain text passwords)
        # ⚠️ This is only for migration - remove after migration
        if plain_password == hashed_password:
            print("⚠️  Warning: Using plain text password comparison. Please migrate passwords!")
            return True
        return False


def set_password(email: str, new_password: str) -> bool:
    """Define uma nova senha para o usuário"""
    # Importação LOCAL para evitar circular import
    from sqlmodel import select
    from ..database import get_session
    from ..models import Person, User

    with get_session() as session:
        # Buscar a pessoa pelo email
        person = session.exec(select(Person).where(Person.email == email)).first()

        if not person:
            return False

        # Buscar ou criar o registro de usuário
        user = session.exec(select(User).where(User.person_id == person.id)).first()

        if not user:
            # Criar novo usuário
            user = User(person_id=person.id)
            session.add(user)

        # Atualizar a senha usando a função existente get_password_hash
        user.password = get_password_hash(new_password)
        session.commit()

        return True


def set_initial_password(email: str, password: str) -> bool:
    """Define a senha inicial para um usuário (alias para set_password)"""
    return set_password(email, password)


def user_exists(email: str) -> bool:
    """Verifica se um usuário existe no sistema"""
    # Importação LOCAL para evitar circular import
    from sqlmodel import select
    from ..database import get_session
    from ..models import Person

    with get_session() as session:
        person = session.exec(select(Person).where(Person.email == email)).first()
        return person is not None


def get_user_by_email(email: str) -> Optional[dict]:
    """Retorna o objeto User pelo email da pessoa"""
    # Importação LOCAL para evitar circular import
    from sqlmodel import select
    from ..database import get_session
    from ..models import Person, User

    with get_session() as session:
        person = session.exec(select(Person).where(Person.email == email)).first()

        if not person:
            return None

        user = session.exec(select(User).where(User.person_id == person.id)).first()

        return user

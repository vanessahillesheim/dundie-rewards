from typing import Optional

from sqlmodel import Session, select

from dundie.models import Balance, Movement, Person, User
from dundie.settings import EMAIL_FROM
from dundie.utils.email import send_email


def add_person(session: Session, instance: Person):
    """
    Salva dados da pessoa no banco de dados.
    """
    existing = session.exec(
        select(Person).where(Person.email == instance.email)
    ).first()
    created = existing is None

    if created:
        session.add(instance)
        session.flush()  # Garante ID
        set_initial_balance(session, instance)
        password = set_initial_password(session, instance)
        send_email(EMAIL_FROM, instance.email, "Sua senha dundie", password)
        return instance, created
    else:
        existing.dept = instance.dept
        existing.role = instance.role
        session.add(existing)
        return existing, created


def set_initial_password(session: Session, instance: Person) -> str:
    """Cria e salva senha"""
    user = User(person=instance)
    session.add(user)
    session.flush()
    return user.password


def set_initial_balance(session: Session, person: Person):
    """Adiciona movimento e envia para balanço"""
    value = 100 if person.role == "Manager" else 500
    add_movement(session, person, value, actor="system")


def add_movement(
    session: Session,
    person: Person,
    value: int,
    actor: Optional[str] = "system",
):
    """
    Adiciona movimento para usuário.
    """
    # 🔥 SOLUÇÃO: Usar no_autoflush para evitar flush prematuro
    with session.no_autoflush:
        # Garantir que actor nunca seja None
        if actor is None:
            actor = "system"

        # Verificar se person está na sessão
        if person not in session:
            person = session.merge(person)

        # Criar movimento (usando person_id em vez do objeto person)
        movement = Movement(person_id=person.id, value=value, actor=actor)
        session.add(movement)

        # 🔥 Importante: flush apenas do movimento, não de tudo
        session.flush([movement])

        # Agora consultar movements com segurança
        movements = session.exec(
            select(Movement).where(Movement.person_id == person.id)
        ).all()

        total = sum(mov.value for mov in movements)

        # Atualizar balance
        existing_balance = session.exec(
            select(Balance).where(Balance.person_id == person.id)
        ).first()

        if existing_balance:
            existing_balance.value = total
            session.add(existing_balance)
        else:
            session.add(Balance(person_id=person.id, value=total))

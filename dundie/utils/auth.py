# dundie/utils/auth.py

import os
from functools import wraps
from typing import Optional

import click
from sqlmodel import select

from dundie.database import get_session
from dundie.models import User, Person
from dundie.utils.user import verify_password
from dundie.utils.session import load_session, save_session


def authenticate(email: str, password: str) -> bool:
    """Verifica se o usuário existe e a senha está correta"""
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == email)
        ).first()
        
        if not person:
            return False
        
        user = session.exec(
            select(User).where(User.person_id == person.id)
        ).first()
        
        if not user:
            return False
        
        return verify_password(password, user.password)


def check_admin_role(email: str) -> tuple:
    """Verifica se o usuário tem role de admin
    
    Retorna: (is_admin: bool, role: str, name: str)
    """
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == email)
        ).first()
        
        if not person:
            return False, None, None
        
        admin_roles = ["Manager", "CEO", "Admin", "C-Level"]
        is_admin = person.role in admin_roles
        
        return is_admin, person.role, person.name


def get_current_user(email: str):
    """Retorna o objeto Person do usuário atual"""
    with get_session() as session:
        person = session.exec(
            select(Person).where(Person.email == email)
        ).first()
        
        if not person:
            return None
        
        return person


def login_required(f):
    """Decorator para proteger comandos que exigem autenticação"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Tentar carregar sessão do arquivo
        email, password = load_session()
        
        if not email or not password:
            # Tentar obter interativamente
            if click.confirm("Authentication required. Do you want to login?"):
                email = click.prompt("Email", type=str)
                password = click.prompt("Password", hide_input=True, type=str)
            else:
                click.echo("Authentication required to perform this operation.")
                return
        
        if not authenticate(email, password):
            click.echo("Invalid credentials.")
            return
        
        # Salvar sessão se foi autenticado
        save_session(email, password)
        
        # Adicionar o objeto Person autenticado ao contexto
        kwargs['current_user'] = get_current_user(email)
        return f(*args, **kwargs)
    
    return wrapper


def admin_required(f):
    """Decorator para proteger comandos que exigem permissão de ADMIN"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Tentar carregar sessão do arquivo
        email, password = load_session()
        
        if not email or not password:
            # Tentar obter interativamente
            if click.confirm("Authentication required. Do you want to login?"):
                email = click.prompt("Email", type=str)
                
                # PRIMEIRO: Verificar se o email existe e tem role de admin
                is_admin, role, name = check_admin_role(email)
                
                if not is_admin:
                    # Se não for admin, já exibe mensagem de acesso negado
                    click.secho("\n❌ ACCESS DENIED!", fg="red", bold=True)
                    click.secho("=" * 50, fg="red")
                    if role:
                        click.secho(f"   User found but without permission.", fg="white")
                        click.secho(f"   Your role: {role}", fg="yellow")
                        click.secho(f"   Required roles: Manager, CEO, Admin, C-Level", fg="yellow")
                    else:
                        click.secho(f"   User with email '{email}' not found.", fg="white")
                    click.secho("=" * 50, fg="red")
                    click.secho("\n   Only users with Manager, CEO, Admin, or C-Level role", fg="white")
                    click.secho("   can perform administrative operations like removing points.\n", fg="white")
                    return
                
                # Se for admin, então pede a senha
                password = click.prompt("Password", hide_input=True, type=str)
            else:
                click.echo("Authentication required to perform this operation.")
                return
        
        # Agora autentica com email e senha
        if not authenticate(email, password):
            click.secho("\n❌ Invalid credentials!", fg="red")
            return
        
        # Salvar sessão se foi autenticado
        save_session(email, password)
        
        # Obter o usuário atual
        current_user = get_current_user(email)
        if not current_user:
            click.echo("User not found.")
            return
        
        # Adicionar ao kwargs e executar
        kwargs['current_user'] = current_user
        return f(*args, **kwargs)
    
    return wrapper


def require_password_verification(f):
    """Decorator que exige verificação de senha para operações sensíveis"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        
        if not current_user:
            return login_required(f)(*args, **kwargs)
        
        # Solicitar senha atual para confirmar a operação
        password = click.prompt(
            "🔐 Please enter your password to confirm this operation",
            hide_input=True,
            type=str
        )
        
        # Buscar o hash da senha do usuário
        with get_session() as session:
            user = session.exec(
                select(User).where(User.person_id == current_user.id)
            ).first()
            
            if not user or not verify_password(password, user.password):
                click.echo("❌ Invalid password. Operation cancelled.")
                return
        
        click.echo("✅ Password verified. Proceeding...")
        return f(*args, **kwargs)
    
    return wrapper
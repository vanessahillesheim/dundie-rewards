# dundie/utils/session.py
"""Gerenciamento de sessão do usuário"""

import os
import json
from pathlib import Path

SESSION_FILE = Path.home() / ".dundie_session"


def save_session(email: str, password: str):
    """Salva a sessão do usuário em um arquivo"""
    session_data = {"email": email, "password": password}
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)
    # Também salva nas variáveis de ambiente (para o processo atual)
    os.environ["DUNDIE_USER"] = email
    os.environ["DUNDIE_PASSWORD"] = password


def load_session() -> tuple:
    """Carrega a sessão do usuário do arquivo"""
    # Primeiro tenta variáveis de ambiente
    email = os.getenv("DUNDIE_USER")
    password = os.getenv("DUNDIE_PASSWORD")

    if email and password:
        return email, password

    # Se não tiver nas variáveis, tenta o arquivo
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, "r") as f:
                session_data = json.load(f)
                # Restaura nas variáveis de ambiente
                os.environ["DUNDIE_USER"] = session_data["email"]
                os.environ["DUNDIE_PASSWORD"] = session_data["password"]
                return session_data["email"], session_data["password"]
        except (json.JSONDecodeError, KeyError):
            # Arquivo corrompido, remove
            SESSION_FILE.unlink()

    return None, None


def clear_session():
    """Limpa a sessão do usuário"""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
    if "DUNDIE_USER" in os.environ:
        del os.environ["DUNDIE_USER"]
    if "DUNDIE_PASSWORD" in os.environ:
        del os.environ["DUNDIE_PASSWORD"]


def is_authenticated() -> bool:
    """Verifica se o usuário está autenticado"""
    email, password = load_session()
    return email is not None and password is not None


def get_session_email() -> str:
    """Retorna o email da sessão atual"""
    email, _ = load_session()
    return email

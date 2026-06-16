"""núcleo do dundie"""

import csv
import os
from typing import Any, Dict, List

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person
from dundie.settings import DATEFMT
from dundie.utils.db import add_movement, add_person
from dundie.utils.exchange import USDRate, get_rates
from dundie.utils.log import get_logger

# configurando Logger
log = get_logger()
Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


def load(filepath: str = None) -> ResultDict:
    """ler as linhas do arquivo e salvar no banco de dados

    Se filepath não for fornecido, usa o arquivo padrão em assets/people.csv
    """
    # Define o caminho padrão se nenhum for fornecido
    if filepath is None:
        # Obtém o diretório base do projeto
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "assets", "people.csv")
        log.info(f"Nenhum arquivo especificado. Usando arquivo padrão: {filepath}")

    try:
        with open(filepath) as file:
            csv_data = csv.reader(file)
            people = []
            headers = ["name", "dept", "role", "email", "currency"]

            with get_session() as session:
                for line in csv_data:
                    person_data = dict(zip(headers, [item.strip() for item in line]))

                    instance = Person(**person_data)
                    person, created = add_person(session, instance)

                    return_data = {
                        "name": person.name,
                        "dept": person.dept,
                        "role": person.role,
                        "email": person.email,
                        "currency": person.currency,
                        "created": created,
                    }
                    people.append(return_data)

                session.commit()
            return people

    except FileNotFoundError as e:
        log.error(str(e))
        raise e


def read(**query: Query) -> ResultDict:
    """Fazer consulta usando como filtro o email ou dept"""
    # Remover None values
    query = {k: v for k, v in query.items() if v is not None}
    return_data = []

    query_statements = []
    if "dept" in query:
        query_statements.append(Person.dept == query["dept"])
    if "email" in query:
        query_statements.append(Person.email == query["email"])

    sql = select(Person)
    if query_statements:
        sql = sql.where(*query_statements)

    with get_session() as session:
        # Busca moedas distintas
        currencies_stmt = select(Person.currency).distinct()
        currencies_result = session.exec(currencies_stmt)
        currencies_list = currencies_result.all()

        # Pega as taxas de câmbio com fallback
        try:
            rates = get_rates(currencies_list)
        except Exception as e:
            log.error(f"Erro ao buscar taxas: {e}")
            # Fallback: taxa 1:1 para todas as moedas
            rates = {c: USDRate(high=1) for c in currencies_list}

        results = session.exec(sql)
        for person in results:
            # CORREÇÃO: balance é um objeto único
            if person.balance:
                balance_value = int(person.balance.value)  # Garantir que é inteiro
                # Converte para USD usando a taxa
                rate_value = rates.get(person.currency, USDRate(high=1)).value
                total_usd = rate_value * balance_value  # Manter como float para decimais
            else:
                balance_value = 0
                total_usd = 0.0

            # CORREÇÃO: movement é um relacionamento que pode retornar lista
            # Precisamos pegar o mais recente se existir
            if person.movement:
                # person.movement pode ser uma lista de movimentos
                # Vamos verificar se é lista ou objeto único
                if hasattr(person.movement, "__iter__") and not isinstance(person.movement, str):
                    # É uma lista, pega o mais recente
                    movements_list = list(person.movement)
                    if movements_list:
                        last_movement_date = movements_list[-1].date
                    else:
                        last_movement_date = None
                else:
                    # É objeto único
                    last_movement_date = person.movement.date
            else:
                last_movement_date = None

            # Prepara os dados da pessoa
            person_data = {
                "email": person.email,
                "name": person.name,
                "dept": person.dept,
                "role": person.role,
                "currency": person.currency,
                "balance": balance_value,  # Inteiro
                "total_usd": round(total_usd, 2),  # Decimal com 2 casas
                "last_movement": (last_movement_date.strftime(DATEFMT) if last_movement_date else None),
            }
            return_data.append(person_data)

    return return_data


def add(value: int, **query: Query):
    """Adicionar pontos para cada filtro: e-mail ou dept"""
    query = {k: v for k, v in query.items() if v is not None}
    people = read(**query)

    if not people:
        raise RuntimeError("not found")

    with get_session() as session:
        user = os.getenv("USER")
        for person in people:
            instance = session.exec(select(Person).where(Person.email == person["email"])).first()
            add_movement(session, instance, value, user)
        session.commit()


# Adicione estas funções no final do arquivo dundie/core.py

from typing import Dict, List, Optional
from sqlmodel import select
from dundie.models import Person, Movement
from dundie.settings import DATEFMT


def transfer(from_user: str, to_email: str, value: int) -> Dict:
    """Transfere pontos de um usuário para outro"""
    if value <= 0:
        return {"success": False, "error": "Value must be positive"}

    with get_session() as session:
        # Buscar usuários
        from_person = session.exec(select(Person).where(Person.email == from_user)).first()

        to_person = session.exec(select(Person).where(Person.email == to_email)).first()

        if not from_person:
            return {"success": False, "error": "Sender not found"}

        if not to_person:
            return {"success": False, "error": "Recipient not found"}

        # Verificar saldo
        if not from_person.balance or from_person.balance.value < value:
            return {"success": False, "error": "Insufficient balance"}

        # Registrar movimentações
        add_movement(session, from_person, -value, actor=from_user)
        add_movement(session, to_person, value, actor=from_user)

        session.commit()

        # Atualizar saldos - forçar refresh
        session.refresh(from_person)
        session.refresh(to_person)

        return {
            "success": True,
            "from_balance": (from_person.balance.value if from_person.balance else 0),
            "to_balance": to_person.balance.value if to_person.balance else 0,
        }


def get_balance(email: str) -> Optional[Dict]:
    """Retorna o saldo do usuário"""
    with get_session() as session:
        person = session.exec(select(Person).where(Person.email == email)).first()

        if not person:
            return None

        return {
            "name": person.name,
            "balance": (int(person.balance.value) if person.balance else 0),  # Garantir inteiro
            "currency": person.currency,
        }


def get_statement(email: str, limit: int = 10) -> List[Dict]:
    """Retorna o extrato de movimentações"""
    with get_session() as session:
        person = session.exec(select(Person).where(Person.email == email)).first()

        if not person:
            return []

        # Buscar movimentos diretamente pela query em vez do relacionamento
        movements = session.exec(
            select(Movement).where(Movement.person_id == person.id).order_by(Movement.date.desc()).limit(limit)
        ).all()

        return [
            {
                "date": mov.date.strftime(DATEFMT),
                "value": mov.value,
                "actor": mov.actor,
            }
            for mov in movements
        ]

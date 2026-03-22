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


def load(filepath: str) -> ResultDict:
    """ler as linhas do arquivo e salvar no banco de dados"""
    try:
        with open(filepath) as file:
            csv_data = csv.reader(file)
            people = []
            headers = ["name", "dept", "role", "email", "currency"]

            with get_session() as session:
                for line in csv_data:
                    person_data = dict(
                        zip(headers, [item.strip() for item in line])
                    )

                    # Agora este bloco está DENTRO do loop for
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
            # CORREÇÃO: balance é um objeto único, não uma lista
            if person.balance:
                balance_value = person.balance.value
                # Converte para USD usando a taxa
                rate_value = rates.get(person.currency, USDRate(high=1)).value
                total_usd = rate_value * balance_value
            else:
                balance_value = 0
                total_usd = 0

            # CORREÇÃO: movement é um objeto único, não uma lista
            if person.movement:
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
                "balance": balance_value,
                "total_usd": round(total_usd, 2),
                "last_movement": (
                    last_movement_date.strftime(DATEFMT)
                    if last_movement_date
                    else None
                ),
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
            instance = session.exec(
                select(Person).where(Person.email == person["email"])
            ).first()
            add_movement(session, instance, value, user)
        session.commit()

"""núcleo do dundie"""

import os
from csv import reader

from dundie.database import add_movement, add_person, commit, connect
from dundie.utils.log import get_logger

# configurando Logger
log = get_logger()


def load(filepath):
    """ler as linhas do arquivo e salvar no banco de dados"""
    try:
        csv_data = reader(open(filepath))
    except FileNotFoundError as e:
        log.error(str(e))
        raise e

    db = connect()
    people = []
    headers = ["name", "dept", "role", "email"]
    for line in csv_data:
        person_data = dict(zip(headers, [item.strip() for item in line]))
        pk = person_data.pop("email")
        person, created = add_person(db, pk, person_data)
        return_data = person.copy()
        return_data["created"] = created
        return_data["email"] = pk
        people.append(return_data)

    commit(db)
    return people


def read(**query):
    """Fazer consulta usando como filtro o email ou dpto

    read(email="test_read_joe@doe.com)
    """
    db = connect()
    return_data = []
    for pk, data in db["people"].items():

        dept = query.get("dept")
        if dept and dept != data["dept"]:
            continue

        if (email := query.get("email")) and email != pk:
            continue

        return_data.append(
            {
                "email": pk,
                "balance": db["balance"][pk],
                "last_movement": db["movement"][pk][-1]["date"],
                **data,
            }
        )
    return return_data


def add(value, **query):
    """Adicionar pontos para cada filtro: e-mail ou dpto"""
    people = read(**query)
    if not people:
        raise RuntimeError("not found")

    db = connect()
    user = os.getenv("USER")
    for person in people:
        add_movement(db, person["email"], value, user)
    commit(db)

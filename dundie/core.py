"""núcleo do dundie"""

from csv import reader

from dundie.database import add_person, commit, connect
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
        # return_data = person.copy()
        person["created"] = created
        person["email"] = pk
        people.append(person)

    commit(db)
    return people

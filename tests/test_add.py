import pytest

from dundie.core import add
from dundie.database import add_person, commit, connect


@pytest.mark.unit
def test_add_movement():
    db = connect()

    # PRIMEIRO: Limpa dados problemáticos de testes anteriores
    problematic_emails = [
        "test_commit_joe@doe.com",  # De test_commit_to_database
        "1testejoe@doe.com",  # De test_add_person_for_the_first_time
        "jim@dundermifflin.com",  # De test_load.py
        "schrute@dundermifflin.com",  # De test_load.py
        "glewis@dundermifflin.com",  # De test_load.py
    ]

    for email in problematic_emails:
        for key in ["people", "balance", "movement", "users"]:
            if email in db[key]:
                del db[key][email]

    commit(db)

    # AGORA: Teste normal com emails únicos
    db = connect()

    pk = "test_read_joe@doe.com"
    data = {"role": "Salesman", "dept": "Sales", "name": "Joe Doe"}
    _, created = add_person(db, pk, data)
    assert created is True
    commit(db)

    pk = "test_read_jim@doe.com"
    data = {"role": "Manager", "dept": "Management", "name": "Jim Doe"}
    _, created = add_person(db, pk, data)
    assert created is True
    commit(db)

    add(-30, email="test_read_joe@doe.com")
    add(90, dept="Management")

    db = connect()
    assert db["balance"]["test_read_joe@doe.com"] == 470
    assert db["balance"]["test_read_jim@doe.com"] == 190

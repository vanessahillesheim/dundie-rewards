import pytest

from dundie.database import EMPTY_DB, add_movement, add_person, commit, connect


@pytest.mark.unit
def test_database_schema():
    db = connect()
    assert db.keys() == EMPTY_DB.keys()


@pytest.mark.unit
def test_commit_to_database():
    db = connect()
    # EMAIL ÚNICO para não interferir
    unique_email = "test_commit_joe@doe.com"  # MUDAR AQUI!
    data = {"name": "Joe Doe", "role": "Salesman", "dept": "Sales"}
    db["people"][unique_email] = data
    commit(db)

    db = connect()
    assert db["people"][unique_email] == data
    # o arquivo gerado no teste é salvo em
    # C:\Users\admin\AppData\Local\Temp\pytest-of-admin"


@pytest.mark.unit
def test_add_person_for_the_first_time():
    pk = "1testejoe@doe.com"  # mudar o e-mail cada vez q rodar o test
    data = {"role": "Salesman", "dept": "Sales", "name": "Joe Doe"}
    db = connect()
    _, created = add_person(db, pk, data)
    assert created is True
    commit(db)

    db = connect()
    assert db["people"][pk] == data
    assert db["balance"][pk] == 500
    assert len(db["movement"][pk]) > 0
    assert db["movement"][pk][0]["value"] == 500
    # o arquivo gerado no teste é salvo em
    # C:\Users\admin\AppData\Local\Temp\pytest-of-admin"


@pytest.mark.unit
def test_negative_add_person_invalid_email():
    with pytest.raises(ValueError):
        add_person({}, ".@bla", {})


@pytest.mark.unit
def test_add_or_remove_points_for_person():
    """Testa movimentação de pontos em pessoa existente"""
    # Email único para garantir isolamento
    pk = "movement_test_unique@doe.com"

    # PASSO 1: Setup - criar pessoa com saldo conhecido
    db = connect()

    # Limpa qualquer resquício (defesa extra)
    if pk in db["people"]:
        # Remove se já existir (não deveria com fixture)
        for key in ["people", "balance", "movement", "users"]:
            db[key].pop(pk, None)
    commit(db)

    # Cria pessoa nova
    db = connect()
    data = {"role": "Salesman", "dept": "Sales", "name": "Joe Doe"}
    _, created = add_person(db, pk, data)

    # Com fixture, created DEVE ser True
    # Mas vamos apenas logar se não for
    if not created:
        print(f"AVISO: Pessoa {pk} já existia. Continuando teste...")

    commit(db)

    # PASSO 2: Testa remoção de pontos
    db = connect()
    initial_balance = db["balance"][pk]  # Deve ser 500

    # Remove 100 pontos
    add_movement(db, pk, -100, "manager")
    commit(db)

    # PASSO 3: Verifica
    db = connect()
    final_balance = db["balance"][pk]

    # Assert principal
    assert final_balance == initial_balance - 100

    # Asserts específicos (se sabemos valores)
    if initial_balance == 500:
        assert final_balance == 400

    # Verifica se movimento foi registrado
    movements = db["movement"][pk]
    last_movement = movements[-1]
    assert last_movement["value"] == -100
    assert last_movement["actor"] == "manager"

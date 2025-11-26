"""Core = testano o corpo de dindie"""
import uuid
import pytest
from dundie.core import load
from .constants import PEOPLE_FILE

def setup_module():
    print()
    print("roda antres dos testes deste módulo. \n")

def teardown_module():
    print()
    print("roda após os testes deste módulo.")

@pytest.fixture(scope="function", autouse=True)
def create_new_file(tmpdir):
    file_ = tmpdir.join("novo arquivo.txt")
    file_.write("isso é sujeira do teste...")
    yield
    file_.remove()

@pytest.mark.unit
@pytest.mark.high

def test_load(request): 
    """Testando a função load"""

    request.addfinalizer(lambda: print("\nTerminou!")) #roda depois da execução da função test_load

    with open(f"arquivo_indesejado-{uuid.uuid4()}.txt", "w") as file_:file_.write("dados úteis somente para o teste")
    assert len(load(PEOPLE_FILE)) == 2
    assert load(PEOPLE_FILE)[0][0] == 'J'

@pytest.mark.unit
@pytest.mark.high

def test_load2(): 
    """Testando a função load"""

    with open(f"arquivo_indesejado-{uuid.uuid4()}.txt", "w") as file_:file_.write("dados úteis somente para o teste")
    assert len(load(PEOPLE_FILE)) == 2
    assert load(PEOPLE_FILE)[0][0] == 'J'

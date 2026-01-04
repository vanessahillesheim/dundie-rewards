import pytest
from unittest.mock import patch

MARKER = """\
unit: Mark unit tests
integration: Mark integration tests
high: High Priority
medium: Medium Priority
low: Low Priority
"""

def pytest_configure(config):
    for line in MARKER.split("\n"):
        config.addinivalue_line("markers", line)


@pytest.fixture(autouse=True)  # fixture faz os prérequisitos para rodar o teste
def go_to_tmpdir(request):  # injeção de dependências
    tmpdir = request.getfixturevalue("tmpdir")
    with tmpdir.as_cwd():
        yield


@pytest.fixture(autouse=True, scope="function")  #para cada teste, criar um arquivo do DB separado
def setup_testing_database(request):
    """Para cada teste, criar um arquivo no tmpdir de banco de dados """
    tmpdir = request.getfixturevalue("tmpdir")
    test_db = str(tmpdir.join("database.test.json"))
    with patch("dundie.database.DATABASE_PATH", test_db):
        yield
    #o arquivo gerado no teste é salvo em C:\Users\admin\AppData\Local\Temp\pytest-of-admin"

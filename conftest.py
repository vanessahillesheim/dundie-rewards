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


@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    """Fixture faz os prérequisitos para rodar o teste."""
    tmpdir = request.getfixturevalue("tmpdir")
    with tmpdir.as_cwd():
        yield

# O arquivo gerado no teste é salvo em
# C:\Users\admin\AppData\Local\Temp\pytest-of-admin


@pytest.fixture(autouse=True, scope="function")
def setup_testing_database(request):
    """Para cada teste, criar um arquivo no tmpdir de banco de dados."""
    tmpdir = request.getfixturevalue("tmpdir")
    test_db = str(tmpdir.join("database.test.json"))
    with patch("dundie.database.DATABASE_PATH", test_db):
        yield

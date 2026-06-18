import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from dundie.cli import main

cmd = CliRunner()

# CORRIGIDO: caminho correto para o arquivo
BASE_DIR = Path(__file__).parent.parent
PEOPLE_FILE = str(BASE_DIR / "assets" / "people.csv")


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Vai testar o comando load."""
    # Verifica se o arquivo existe
    print(f"\n[DEBUG] PEOPLE_FILE: {PEOPLE_FILE}")
    print(f"[DEBUG] File exists: {os.path.exists(PEOPLE_FILE)}")

    # CORRIGIDO: usa o caminho correto
    out = cmd.invoke(main, ["load", PEOPLE_FILE])

    if out.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {out.exit_code}")
        print(f"[DEBUG] Output: {out.output[:500]}")
        print(f"[DEBUG] Exception: {out.exception}")

    assert out.exit_code == 0
    assert "Funcionários Carregados" in out.output

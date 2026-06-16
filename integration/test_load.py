import os

import pytest
from click.testing import CliRunner

from dundie.cli import main
from integration.constants import PEOPLE_FILE

cmd = CliRunner()


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Vai testar o comando load."""
    # Verifica se o arquivo existe
    print(f"\n[DEBUG] PEOPLE_FILE: {PEOPLE_FILE}")
    print(f"[DEBUG] File exists: {os.path.exists(PEOPLE_FILE)}")

    out = cmd.invoke(main, ["load", PEOPLE_FILE])

    # Debug se necessário
    if out.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {out.exit_code}")
        print(f"[DEBUG] Output: {out.output[:500]}")
        print(f"[DEBUG] Exception: {out.exception}")

    assert out.exit_code == 0
    assert "Dunder Mifflin Associates" in out.output

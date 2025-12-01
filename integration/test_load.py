from click.testing import CliRunner
from dundie.cli import main
import pytest

from tests.constants import PEOPLE_FILE

cmd = CliRunner()

@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """vai testar o comando load"""
    out = cmd.invoke(main, ["load", PEOPLE_FILE])
    
    # Debug se necessário
    if out.exit_code != 0:
        print(f"\n[DEBUG] Exit code: {out.exit_code}")
        print(f"[DEBUG] Output: {out.output[:500]}")
    
    assert out.exit_code == 0
    assert "Dunder Mifflin Associates" in out.output

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """vai testar o comando load"""
    out = cmd.invoke(main, [wrong_command, PEOPLE_FILE])
    assert out.exit_code != 0
    assert f"No such command '{wrong_command}'." in out.output


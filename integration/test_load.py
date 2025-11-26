

import pytest
from subprocess import check_output, CalledProcessError

@pytest.mark.integration
@pytest.mark.medium


def test_load_positive_call_load_command():
    """vai terar o comando load"""
    out = check_output(["dundie", "load", "tests/assets/people.csv"]).decode("utf-8").split("\n")
    # Remove linhas vazias do final
    out = [line for line in out if line.strip()]
    
    # Agora deve ter 2 linhas com conteúdo
    assert len(out) == 2
    assert "initializing dundie" in out[0].lower()
    assert "jim halpert" in out[1].lower()

@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize("wrong_command", ["loady", "carrega", "start"])
#se digitar loady ao invés de load no terminal: dundie loady assets/people.csv
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """vai terar o comando load"""
    with pytest.raises(CalledProcessError) as error:

        out = check_output(
            ["dundie", wrong_command, "tests/assets/people.csv"]).decode("utf-8").split("\n")
    assert "status 2" in str(error.getrepr())

      


import pytest
from subprocess import check_output

@pytest.mark.integration
@pytest.mark.medium

def test_load():
    """vai terar o comando load"""
    out = check_output(["dundie", "load", "tests/assets/people.csv"]).decode("utf-8").split("\n")
    # Remove linhas vazias do final
    out = [line for line in out if line.strip()]
    
    # Agora deve ter 2 linhas com conteúdo
    assert len(out) == 2
    assert "initializing dundie" in out[0].lower()
    assert "jim halpert" in out[1].lower()
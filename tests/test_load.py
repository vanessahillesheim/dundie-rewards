"""Core = testano o corpo de dindie"""
import uuid
import pytest
from dundie.core import load
from .constants import PEOPLE_FILE

@pytest.mark.unit
@pytest.mark.high

def test_load_positive_has_3_people(request): 
    """Testando a função load"""
    assert len(load(PEOPLE_FILE)) == 3
    

@pytest.mark.unit
@pytest.mark.high
def test_load_positive_first_name_starts_with_j(request): 
    assert load(PEOPLE_FILE)[0][0] == 'J'


import httpx
from decimal import Decimal
from typing import List, Dict
from dundie.settings import API_BASE_URL
from pydantic import BaseModel, Field
import logging

log = logging.getLogger(__name__)

class USDRate(BaseModel):
    code: str = Field(default="USD")
    codein: str = Field(default="USD")
    name: str = Field(default="Dolar/Dolar")
    value: Decimal = Field(alias="high")

def get_rates(currencies: List[str]) -> Dict[str, USDRate]:
    """Gets current rate for USD vs Currency"""
    return_data = {}
    
    for currency in currencies:
        if currency == "USD":
            return_data[currency] = USDRate(high=1)
        else:
            try:
                url = API_BASE_URL.format(currency=currency)
                log.info(f"Tentando acessar: {url}")
                
                with httpx.Client(timeout=10.0) as client:
                    response = client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    # A API retorna com a chave no formato USD{currency}
                    key = f"USD{currency}"
                    
                    if key in data:
                        # Pega os dados da moeda específica
                        currency_data = data[key]
                        return_data[currency] = USDRate(**currency_data)
                    else:
                        log.error(f"Chave {key} não encontrada no response: {data.keys()}")
                        return_data[currency] = USDRate(name="api/error", high=0)
                else:
                    log.error(f"Erro HTTP {response.status_code} para {currency}")
                    return_data[currency] = USDRate(name="api/error", high=0)
                    
            except Exception as e:
                log.error(f"Erro ao buscar taxa para {currency}: {e}")
                return_data[currency] = USDRate(name="error", high=0)
    
    return return_data
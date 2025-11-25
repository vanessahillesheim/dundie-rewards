"""núcleo do dundie"""

import logging

#configurando Logger
log = logging.getLogger(__name__)

def load(filepath):
    """ler as linhas do arquivo e salvar no banco de dados"""
    try:
        with open(filepath) as file_:
            return [line.strip() for line in file_.readlines()]
    except FileNotFoundError as e:
        log.error(str(e))
        raise e
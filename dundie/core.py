"""núcleo do dundie"""

def load(filepath):
    """ler as linhas do arquivo e salvar no banco de dados"""
    try:
        with open(filepath) as file_:
            return file_.readlines()
    except FileNotFoundError as e:
        log.error(str(e))
        raise e
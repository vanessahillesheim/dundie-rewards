import argparse
from dundie.core import load # noqa


# para rodar o arquivo, no terminal digitar: dundie load people.csv
def main():
    parser = argparse.ArgumentParser(
        description="Dunder Mifflin Rewards CLI",
        epilog="Enjoy and use with cautions,",
    )

    # aqui vai rodar o subcomando "load"
    parser.add_argument(
        "subcommand",
        type=str,
        help="The subcomand to run",
        # para iniciar, mostrar e enviar pontos
        choices=("load", "show", "send"),
        default="help"
    )
    # aqui é o caminho do arquivo "people.csv"
    parser.add_argument(
        "filepath",
        type=str,
        help="Filepath to load",
        default=None
    )
    args = parser.parse_args()
    print(*globals()[args.subcommand](args.filepath))

# interface com o usuário
import json
import os
from importlib.metadata import version

import pkg_resources
import rich_click as click
from rich.console import Console
from rich.table import Table

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


# para rodar o arquivo, no terminal digitar: dundie load assets/people.csv
@click.group()
@click.version_option(pkg_resources.get_distribution("dundie").version)
def main():
    """
    Dunder Mifflin Rewards System.

    This cli application controls DM rewards.
    """


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath):
    """Loads the file to the database.

    ## Features
    - Validates data
    - Parses the file
    - Loads to database
    """
    table = Table(title="Dunder Mifflin Associates")
    headers = ["name", "dpto", "role", "created", "e-mail"]
    for header in headers:
        table.add_column(header, style="magenta")

    result = core.load(filepath)
    for person in result:
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


# para expor a tabela de pontos de um usuário já cadastrado, no terminal:
# dundie show --email=jim@dundermifflin.com
# dundie show  -> aparecem todos os usuários cadastrados
# dundie show --dept=Sale  -> apenas usuário do depto Sale
@main.command()
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.option("--output", default=None)
def show(output, **query):
    """Mostras as informações dos usuários"""
    result = core.read(**query)

    # dundie show --output="C:\temp\balanco.json"
    # o comando acima vai gerar um arquivo json com o balanço dos pontos
    if output:
        # Garante que os diretórios existam
        output_path = os.path.abspath(output)
        directory = os.path.dirname(output_path)
        if directory:  # Se o caminho tem diretórios
            os.makedirs(directory, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(result, output_file, indent=2)
        click.echo(f"Arquivo salvo em: {output_path}")

    if not result:
        print("Nothing to show.")

    # para visualizar os pontos de cada usuário/dpto
    table = Table(title="Dunder Mifflin Report")
    for key in result[0]:
        table.add_column(key.title(), style="magenta")

    for person in result:
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


# para adicionar pontos ao depto "sales", digitar no terminal:
# dundie add 50 --dept=Sales
@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context  # context vai gerar o show para mostrar balanço atualizado
def add(ctx, value, **query):
    """Adiciona pontos aos usuários/depto"""
    core.add(value, **query)
    ctx.invoke(show, **query)


# para remover pontos ao depto "sales", digitar no terminal:
# dundie remove 50 --dept=Sales
@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value, **query):
    """Adiciona pontos aos usuários/depto"""
    core.add(-value, **query)
    ctx.invoke(show, **query)

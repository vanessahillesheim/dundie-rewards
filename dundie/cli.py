# interface com o usuário
import json
import os
from importlib.metadata import version  # ✅ Apenas esta importação

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


@click.group()
@click.version_option(version("dundie"))
def main():
    """
    Dunder Mifflin Rewards System.

    Este aplicativo CLI controla as recompensas da DM.

    * administradores podem carregar informações no banco de dados de pessoas
     e atribuir pontos.
    * usuário pode visualizar relatórios e transferência de pontos.
    """


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath):
    """Carrega o arquivo do banco de dados."""
    table = Table(title="Dunder Mifflin Associates")
    
    # Headers na MESMA ordem do return_data em core.load()
    # E com os nomes bonitos para exibição
    headers_order = ["name", "dept", "role", "email", "currency", "created"]
    display_headers = {
        "name": "Name",
        "dept": "Department",
        "role": "Role",
        "email": "E-mail",
        "currency": "Currency",
        "created": "Created"
    }
    
    for header in headers_order:
        table.add_column(display_headers[header], style="magenta")

    result = core.load(filepath)
    for person in result:
        # Construir a linha na ordem exata dos headers_order
        row = [
            str(person.get("name", "")),
            str(person.get("dept", "")),
            str(person.get("role", "")),
            str(person.get("email", "")),
            str(person.get("currency", "USD")),
            str(person.get("created", ""))
        ]
        table.add_row(*row)

    console = Console()
    console.print(table)


@main.command()
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.option("--output", default=None)
def show(output, **query):
    """Mostra as informações dos usuários/depto"""
    result = core.read(**query)

    if output:
        # Garante que os diretórios existam
        output_path = os.path.abspath(output)
        directory = os.path.dirname(output_path)
        if directory:  # Se o caminho tem diretórios
            os.makedirs(directory, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(result, output_file, indent=2, ensure_ascii=False)
        click.echo(f"Arquivo salvo em: {output_path}")

    if not result:
        click.echo("Nothing to show.")
        return
    
    # para visualizar os pontos de cada usuário/dpto
    table = Table(title="Dunder Mifflin Report")
    for key in result[0]:
        table.add_column(key.title(), style="magenta")

    for person in result:
        # Converte None para string vazia para evitar erros
        row = [str(value) if value is not None else "" for value in person.values()]
        table.add_row(*row)

    console = Console()
    console.print(table)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def add(ctx, value, **query):
    """Adiciona pontos aos usuários/depto"""
    core.add(value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value, **query):
    """Remove pontos aos usuários/depto"""
    core.add(-value, **query)
    ctx.invoke(show, **query)
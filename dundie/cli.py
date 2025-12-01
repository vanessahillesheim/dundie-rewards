import rich_click as click
import pkg_resources
from rich.table import Table
from rich.console import Console

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
    headers = ["name", "depto", "role", "e-mail"]
    for header in headers:
        table.add_column(header, style="magenta")
    
    result = core.load(filepath)
    for person in result:
        table.add_row(*[field.strip() for field in person.split(",")])

    console = Console()
    console.print(table)

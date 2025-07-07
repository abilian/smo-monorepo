import os

import click
from rich.console import Console

from smo_cli.core.config import (
    CONFIG_FILE,
    DB_FILE,
    DEFAULT_SMO_DIR,
    create_default_config,
    get_config_file,
    get_db_file,
    get_smo_dir,
)
from smo_cli.core.database import init_db


@click.command()
def init():
    """Initializes the SMO-CLI environment in ~/.smo/"""
    console = Console()
    smo_dir = get_smo_dir()
    config_file = get_config_file()
    db_file = get_db_file()

    console.print(f"Initializing SMO-CLI environment in [cyan]{smo_dir}[/]...")
    if not os.path.exists(smo_dir):
        os.makedirs(smo_dir)
        console.print(f"  -> Created directory: [green]{smo_dir}[/green]")

    if not os.path.exists(config_file):
        create_default_config()
        console.print(
            f"  -> Created default configuration file: [green]{config_file}[/green]"
        )
        console.print(
            "  -> [bold yellow]IMPORTANT:[/] Please edit this file to match your environment.",
            style="yellow",
        )
    else:
        console.print(
            f"  -> Configuration file already exists: [yellow]{config_file}[/yellow]"
        )

    # Initialize the database using the engine from the core.database module
    init_db()
    console.print(f"  -> Ensured local database is created: [green]{db_file}[/green]")

    console.print("\n[bold green]Initialization complete.[/bold green]")

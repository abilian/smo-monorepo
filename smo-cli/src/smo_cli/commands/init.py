import os

import click
from rich.console import Console

from smo_cli.core.config import (
    CONFIG_FILE,
    DB_FILE,
    DEFAULT_SMO_DIR,
    create_default_config,
)
from smo_cli.core.database import init_db


@click.command()
def init():
    """Initializes the SMO-CLI environment in ~/.smo/"""
    console = Console()
    console.print(f"Initializing SMO-CLI environment in [cyan]{DEFAULT_SMO_DIR}[/]...")
    if not os.path.exists(DEFAULT_SMO_DIR):
        os.makedirs(DEFAULT_SMO_DIR)
        console.print(f"  -> Created directory: [green]{DEFAULT_SMO_DIR}[/green]")

    if not os.path.exists(CONFIG_FILE):
        create_default_config()
        console.print(
            f"  -> Created default configuration file: [green]{CONFIG_FILE}[/green]"
        )
        console.print(
            "  -> [bold yellow]IMPORTANT:[/] Please edit this file to match your environment.",
            style="yellow",
        )
    else:
        console.print(
            f"  -> Configuration file already exists: [yellow]{CONFIG_FILE}[/yellow]"
        )

    # Initialize the database using the engine from the core.database module
    init_db()
    console.print(f"  -> Ensured local database is created: [green]{DB_FILE}[/green]")

    console.print("\n[bold green]Initialization complete.[/bold green]")

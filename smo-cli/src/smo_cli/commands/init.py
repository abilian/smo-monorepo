import os

import click
from rich.console import Console

from smo_cli.core.config import Config
from smo_cli.core.database import DbManager


@click.command()
def init():
    """Initializes the SMO-CLI environment in ~/.smo/"""
    _init()


def _init():
    console = Console()

    try:
        config = Config.load()
    except FileNotFoundError:
        console.print("[blue]Creating default configuration...[/blue]")
        Config.create_default_config()
        config = Config.load()

    smo_dir = config.smo_dir
    config_file = config.path
    db_file = config.db_file

    console.print(f"Initializing SMO-CLI environment in [cyan]{smo_dir}[/]...")
    if not os.path.exists(smo_dir):
        os.makedirs(smo_dir)
        console.print(f"  -> Created directory: [green]{smo_dir}[/green]")

    if not os.path.exists(config_file):
        Config.create_default_config()
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
    db_manager = DbManager(config)
    db_manager.init_db()
    console.print(f"  -> Ensured local database is created: [green]{db_file}[/green]")

    console.print("\n[bold green]Initialization complete.[/bold green]")

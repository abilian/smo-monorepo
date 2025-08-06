import os

import click
from dishka import FromDishka

from smo_cli.config import Config
from smo_cli.console import Console
from smo_cli.database import DbManager


@click.command()
def init(console: FromDishka[Console]):
    """Initializes the SMO-CLI environment in ~/.smo/"""
    do_init(console)


def do_init(console: Console):
    try:
        config = Config.load()
    except FileNotFoundError:
        console.info("Creating default configuration...")
        Config.create_default_config()
        config = Config.load()

    smo_dir = config.smo_dir
    config_file = config.path
    db_file = config.db_file

    console.info(f"Initializing SMO-CLI environment in [cyan]{smo_dir}[/]...")
    if not os.path.exists(smo_dir):
        os.makedirs(smo_dir)
        console.info(f"  -> Created directory: [green]{smo_dir}[/green]")

    if not os.path.exists(config_file):
        Config.create_default_config()
        console.info(
            f"  -> Created default configuration file: [green]{config_file}[/green]"
        )
        console.info(
            "  -> [bold yellow]IMPORTANT:[/] Please edit this file to match your environment.",
        )
    else:
        console.info(
            f"  -> Configuration file already exists: [yellow]{config_file}[/yellow]"
        )

    # Initialize the database using the engine from the core.database module
    db_manager = DbManager(config)
    db_manager.init_db()
    console.info(f"  -> Ensured local database is created: [green]{db_file}[/green]")

    console.success("\nInitialization complete.")

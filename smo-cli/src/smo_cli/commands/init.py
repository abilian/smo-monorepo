import os
from pathlib import Path

import click
from dishka import FromDishka
from sqlalchemy import Engine

from smo_cli import config
from smo_cli.config import Config
from smo_cli.console import Console
from smo_core.models.base import Base


@click.command
def init(engine: FromDishka[Engine], console: FromDishka[Console]):
    """Initializes the SMO-CLI environment in ~/.smo/ or $SMO_DIR/"""
    do_init(engine, console)


def do_init(engine: Engine, console: Console):
    config = Config.load()

    if config.path is None:
        create_config(console)

    # Initialize the database
    Base.metadata.create_all(bind=engine)
    console.info(
        f"  -> Ensured local database is created: [green]{config.db_url}[/green]"
    )

    console.success("\nInitialization complete.")


def create_config(console: Console):
    if "SMO_DIR" in os.environ:
        smo_dir = Path(os.environ["SMO_DIR"]).expanduser()
    else:
        smo_dir = config.DEFAULT_SMO_DIR

    console.info(f"Initializing SMO-CLI environment in [cyan]{smo_dir}[/]...")
    if not os.path.exists(smo_dir):
        os.makedirs(smo_dir)
        console.info(f"  -> Created directory: [green]{smo_dir}[/green]")

    config_path = smo_dir / config.CONFIG_FILENAME

    if not config_path.exists():
        Config.create_default_config(config_path)
        console.info(
            f"  -> Created default configuration file: [green]{config_path}[/green]"
        )
        console.info(
            "  -> [bold yellow]IMPORTANT:[/] Please edit this file to match your environment.",
        )
    else:
        console.info(
            f"  -> Configuration file already exists: [yellow]{config_path}[/yellow]"
        )

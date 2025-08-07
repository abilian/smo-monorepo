import click
from dishka import FromDishka
from sqlalchemy import Engine

from smo_cli.config import Config, DefaultConfig
from smo_cli.console import Console
from smo_core.models.base import Base


@click.command
def init(engine: FromDishka[Engine], console: FromDishka[Console]):
    """Initializes the SMO-CLI environment in ~/.smo/ or $SMO_DIR/"""
    do_init(engine, console)


def do_init(engine: Engine, console: Console):
    config = Config.load()

    if isinstance(config, DefaultConfig):
        console.info(
            f"Initializing SMO-CLI environment in [cyan]{config.smo_dir}[/]..."
        )
        config.write_default_config()
        console.info(
            f"  -> Created default configuration file: [green]{config.path}[/green]"
        )
        console.info(
            "  -> [bold yellow]IMPORTANT:[/] Please edit this file to match your environment.",
        )
    else:
        console.info(
            f"  -> Configuration file already exists: [yellow]{config.path}[/yellow]"
        )

    # Initialize the database
    Base.metadata.create_all(bind=engine)
    url = engine.url
    console.info(f"  -> Ensured local database is created: [green]{url}[/green]")

    console.success("Initialization complete.")

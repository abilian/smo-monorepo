import pprint

import click
from dishka import FromDishka

from smo_cli.config import Config
from smo_cli.console import Console


@click.command()
def config(console: FromDishka[Console]):
    """Initializes the SMO-CLI environment in ~/.smo/"""
    config = Config.load()
    console.print("Current configuration:")
    console.print(pprint.pformat(config.data))

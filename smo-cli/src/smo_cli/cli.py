import click
from dishka import make_container
from dishka.integrations.click import setup_dishka

from .providers import main_providers


@click.group()
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Enable verbose output. -v for info, -vv for debug.",
)
@click.pass_context
def main(ctx: click.Context, verbosity: int):
    """
    smo-cli: A command-line interface for the Synergetic Meta-Orchestrator.
    """
    container = make_container(*main_providers, context={int: verbosity})
    setup_dishka(container=container, context=ctx, auto_inject=True)


from .commands.cluster import cluster
from .commands.graph import graph
from .commands.init import init
from .commands.scaler import scaler
from .commands.config import config

main.add_command(init)
main.add_command(cluster)
main.add_command(graph)
main.add_command(scaler)
main.add_command(config)

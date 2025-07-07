import click

from .commands.cluster import cluster
from .commands.graph import graph
from .commands.init import init


@click.group()
def main():
    """
    SMO-CLI: A command-line interface for the Synergetic Meta-Orchestrator.
    """


# Add commands and command groups from other files
main.add_command(init)
main.add_command(cluster)
main.add_command(graph)

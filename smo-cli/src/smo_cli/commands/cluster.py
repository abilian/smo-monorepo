import sys
from typing import Iterable

import click
from rich.console import Console
from rich.table import Table

from smo_cli.core.context import CliContext, pass_context
from smo_core.models.cluster import Cluster
from smo_core.services import cluster_service

console = Console()


@click.group()
def cluster():
    """Commands for managing cluster information."""
    pass


@cluster.command()
@pass_context
def sync(ctx: CliContext):
    """Fetches cluster info from Karmada and syncs with the local DB."""
    console.print("Syncing cluster information from Karmada...", style="cyan")
    try:
        with ctx.db_session() as session:
            clusters = cluster_service.fetch_clusters(ctx.core_context, session)
    except Exception as e:
        console.print(f"[bold red]Error syncing clusters:[/] {e}")
        sys.exit(1)

    console.print(f"[green]Successfully synced {len(clusters)} cluster(s).[/green]")
    show_clusters(clusters)


@cluster.command(name="list")
@pass_context
def list_clusters(ctx: CliContext):
    """Lists all clusters known to SMO-CLI from the local DB."""
    try:
        with ctx.db_session() as session:
            clusters = session.query(Cluster).all()

        if not clusters:
            console.print(
                "No clusters found. Run 'smo-cli cluster sync' first.", style="yellow"
            )
            return

        show_clusters(clusters)
    except Exception as e:
        console.print(f"[bold red]Error listing clusters:[/] {e}")
        sys.exit(1)


def show_clusters(clusters):
    table = Table(title="Clusters")
    table.add_column("Name", style="cyan")
    table.add_column("Location", style="white")
    table.add_column("CPU (Avail)", style="magenta")
    table.add_column("RAM (Avail)", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("GPU", style="blue")

    for c in clusters:
        if not isinstance(c, dict):
            c = c.to_dict()
        availability = (
            "[green]Ready[/green]" if c["availability"] else "[red]Not Ready[/red]"
        )
        acceleration = "Yes" if c["acceleration"] else "No"
        table.add_row(
            c["name"],
            c["location"],
            str(c["available_cpu"]),
            c["available_ram"],
            availability,
            acceleration,
        )
    console.print(table)

import click
from dishka.integrations.click import FromDishka
from rich.table import Table

from smo_cli.console import Console
from smo_core.services.cluster_service import ClusterService


@click.group()
def cluster():
    """Commands for managing cluster information."""
    pass


@cluster.command()
def sync(
    console: FromDishka[Console],
    cluster_service: FromDishka[ClusterService],
):
    """Fetches cluster info from Karmada and syncs with the local DB."""
    console.info("Syncing cluster information from Karmada...")
    clusters = cluster_service.fetch_clusters()
    console.success(f"Successfully synced {len(clusters)} cluster(s).")
    table = make_table(clusters)
    console.print(table)


@cluster.command(name="list")
def list_clusters(
    console: FromDishka[Console],
    cluster_service: FromDishka[ClusterService],
):
    """Lists all clusters known to SMO-CLI from the local DB."""
    clusters = cluster_service.list_clusters()
    if not clusters:
        console.warning("No clusters found. Run 'smo-cli cluster sync' first.")
        return

    table = make_table(clusters)
    console.print(table)


def make_table(clusters):
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
    return table

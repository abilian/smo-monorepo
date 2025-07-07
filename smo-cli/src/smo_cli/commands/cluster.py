import click
from rich.console import Console
from rich.table import Table

from smo_cli.core.context import CliContext, pass_context
from smo_core.models.cluster import Cluster
from smo_core.services import cluster_service


@click.group()
def cluster():
    """Commands for managing cluster information."""
    pass


@cluster.command()
@pass_context
def sync(ctx: CliContext):
    """Fetches cluster info from Karmada and syncs with the local DB."""
    console = Console()
    console.print("Syncing cluster information from Karmada...", style="cyan")
    try:
        with ctx.db_session() as session:
            updated_clusters = cluster_service.fetch_clusters(ctx.core_context, session)

        console.print(
            f"[green]Successfully synced {len(updated_clusters)} cluster(s).[/green]"
        )

        table = Table(title="Synced Cluster Status")
        table.add_column("Name", style="cyan")
        table.add_column("Available CPU", style="magenta")
        table.add_column("Available RAM", style="yellow")
        table.add_column("Availability", style="green")

        for c in updated_clusters:
            availability = (
                "[green]Available[/green]"
                if c["availability"]
                else "[red]Not Ready[/red]"
            )
            table.add_row(
                c["name"], str(c["available_cpu"]), c["available_ram"], availability
            )
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error syncing clusters:[/] {e}")


@cluster.command(name="list")
@pass_context
def list_clusters(ctx: CliContext):
    """Lists all clusters known to SMO-CLI from the local DB."""
    console = Console()
    try:
        with ctx.db_session() as session:
            clusters = session.query(Cluster).all()

        if not clusters:
            console.print(
                "No clusters found. Run 'smo-cli cluster sync' first.", style="yellow"
            )
            return

        table = Table(title="Known Clusters")
        table.add_column("Name", style="cyan")
        table.add_column("Location", style="white")
        table.add_column("CPU (Avail)", style="magenta")
        table.add_column("RAM (Avail)", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("GPU", style="blue")

        for c in clusters:
            cluster_dict = c.to_dict()
            availability = (
                "[green]Ready[/green]"
                if cluster_dict["availability"]
                else "[red]Not Ready[/red]"
            )
            acceleration = "Yes" if cluster_dict["acceleration"] else "No"
            table.add_row(
                cluster_dict["name"],
                cluster_dict["location"],
                str(cluster_dict["available_cpu"]),
                cluster_dict["available_ram"],
                availability,
                acceleration,
            )
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error listing clusters:[/] {e}")

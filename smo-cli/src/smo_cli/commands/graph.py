import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from smo_cli.core.context import CliContext, pass_context
from smo_core.models.hdag.graph import Graph
from smo_core.services.hdag import graph_service

console = Console()


@click.group()
def graph():
    """Commands for managing HDAGs."""
    pass


@graph.command()
@click.argument("descriptor", type=click.STRING)
@click.option("--project", required=True, help="The project/namespace for the graph.")
@pass_context
def deploy(ctx: CliContext, descriptor: str, project: str):
    """Deploys a new HDAG from a file or OCI URL."""
    console.print(
        f"Deploying graph from [cyan]'{descriptor}'[/cyan] into project [magenta]'{project}'[/magenta]..."
    )
    try:
        if descriptor.startswith("oci://"):
            graph_data = graph_service.get_descriptor_from_artifact(
                ctx.core_context, project, descriptor
            )
        else:
            with open(descriptor, "r") as f:
                graph_data = yaml.safe_load(f)

        if not graph_data or "hdaGraph" not in graph_data:
            console.print(
                "[bold red]Error:[/] Invalid HDAG descriptor format.", style="red"
            )
            return

        with ctx.db_session() as session:
            graph_service.deploy_graph(
                ctx.core_context, session, project, graph_data["hdaGraph"]
            )

        console.print(
            f"[green]Successfully triggered deployment for graph '{graph_data['hdaGraph']['id']}'.[/green]"
        )
        console.print("Use 'smo-cli graph list' to check status.")
    except Exception as e:
        console.print(f"[bold red]Error during deployment:[/] {e}")


@graph.command(name="list")
@click.option("--project", help="Filter graphs by project.")
@pass_context
def list_graphs(ctx: CliContext, project: str):
    """Lists all deployed graphs."""
    try:
        with ctx.db_session() as session:
            graphs = (
                graph_service.fetch_project_graphs(session, project)
                if project
                else session.query(Graph).all()
            )

        if not graphs:
            msg = "No graphs found."
            if project:
                msg += f" in project '{project}'."
            console.print(msg, style="yellow")
            return

        table = Table(title="Deployed Graphs")
        table.add_column("Name", style="cyan")
        table.add_column("Project", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Services", style="green")

        for g_data in graphs:
            g = g_data if isinstance(g_data, dict) else g_data.to_dict()
            num_services = len(g.get("services", []))
            table.add_row(g["name"], g["project"], g["status"], str(num_services))
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error listing graphs:[/] {e}")


@graph.command()
@click.argument("name", type=click.STRING)
@pass_context
def describe(ctx: CliContext, name: str):
    """Shows detailed information for a specific graph."""
    try:
        with ctx.db_session() as session:
            graph_obj = graph_service.fetch_graph(session, name)

        if not graph_obj:
            console.print(f"Graph [bold red]'{name}'[/bold red] not found.")
            return

        g = graph_obj.to_dict()
        panel_content = (
            f"[bold cyan]Name:[/] {g['name']}\n"
            f"[bold magenta]Project:[/] {g['project']}\n"
            f"[bold yellow]Status:[/] {g['status']}\n"
            f"[bold blue]Grafana:[/] {g.get('grafana', 'N/A')}"
        )
        console.print(
            Panel(
                panel_content, title="Graph Details", border_style="green", expand=False
            )
        )

        if g.get("services"):
            table = Table(title="Services")
            table.add_column("Service Name", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Cluster Affinity", style="magenta")
            table.add_column("Artifact", style="white")
            for svc in g["services"]:
                table.add_row(
                    svc["name"],
                    svc["status"],
                    svc.get("cluster_affinity") or "N/A",
                    svc["artifact_ref"],
                )
            console.print(table)

        if g.get("hdaGraph"):
            yaml_content = yaml.dump(g["hdaGraph"])
            console.print(
                Panel(
                    Syntax(yaml_content, "yaml", theme="monokai"),
                    title="HDAG Descriptor",
                    border_style="blue",
                )
            )
    except Exception as e:
        console.print(f"[bold red]Error describing graph:[/] {e}")


@graph.command()
@click.argument("name", type=click.STRING)
@pass_context
def remove(ctx: CliContext, name: str):
    """Removes a graph completely from SMO and the cluster."""
    if not click.confirm(
        f"Are you sure you want to permanently remove graph '{name}'? This action cannot be undone.",
        abort=True,
    ):
        return
    console.print(f"Removing graph [cyan]'{name}'[/cyan]...", style="red")
    try:
        with ctx.db_session() as session:
            graph_service.remove_graph(ctx.core_context, session, name)
        console.print(f"[green]Graph '{name}' removed successfully.[/green]")
    except Exception as e:
        console.print(f"[bold red]Error removing graph:[/] {e}")


# Add other commands (stop, start, re-place, etc.) following the same pattern...
# For brevity, I'll add one more example: re-place


@graph.command(name="re-place")
@click.argument("name", type=click.STRING)
@pass_context
def re_place(ctx: CliContext, name: str):
    """Triggers placement optimization for a deployed graph."""
    console.print(
        f"Triggering re-placement for graph [cyan]'{name}'[/cyan]...", style="cyan"
    )
    try:
        with ctx.db_session() as session:
            graph_service.trigger_placement(ctx.core_context, session, name)
        console.print(
            f"[green]Re-placement for graph '{name}' completed successfully.[/green]"
        )
        console.print("Check new placement with 'smo-cli graph describe'.")
    except Exception as e:
        console.print(f"[bold red]Error during re-placement:[/] {e}")

import sys
from typing import Iterable

import click
import yaml
from dishka.integrations.click import FromDishka
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from smo_cli.console import Console
from smo_core.models.graph import Graph
from smo_core.services.graph_service import (
    GraphService,
    get_graph_from_artifact,
)

from .exceptions import CliException


@click.group()
def graph():
    """Commands for managing HDAGs."""
    pass


@graph.command()
@click.argument("descriptor", type=click.STRING)
@click.option("--project", required=True, help="The project/namespace for the graph.")
def deploy(
    descriptor: str,
    project: str,
    console: FromDishka[Console],
    graph_service: FromDishka[GraphService],
):
    """Deploys a new HDAG from a file or OCI URL."""
    console.info(f"Deploying graph from '{descriptor}' into project '{project}'...")
    graph_data = get_graph_data(descriptor)

    if not graph_data or "hdaGraph" not in graph_data:
        console.error("Error: Invalid HDAG descriptor format.")
        sys.exit(1)

    graph_service.deploy_graph(project, graph_data["hdaGraph"])

    console.success(
        f"Successfully triggered deployment for graph '{graph_data['hdaGraph']['id']}'."
    )
    console.info("Use 'smo-cli graph list' to check status.")


@graph.command(name="list")
@click.option("--project", help="Filter graphs by project.")
def list_graphs(
    project: str,
    graph_service: FromDishka[GraphService],
    console: FromDishka[Console],
):
    """Lists all deployed graphs."""
    try:
        graphs = graph_service.get_graphs(project) if project else []
        if not project:
            # This part of the logic needs to be on the service
            graphs = graph_service.db_session.query(Graph).all()

        if not graphs:
            msg = "No graphs found."
            if project:
                msg += f" in project '{project}'."
            console.print(msg, style="yellow")
            return

        show_graphs(graphs, console)
    except Exception as e:
        console.error(f"Error listing graphs:\n[black]{e}[/black]")
        sys.exit(1)


@graph.command()
@click.argument("name", type=click.STRING)
def describe(
    name: str, graph_service: FromDishka[GraphService], console: FromDishka[Console]
):
    """Shows detailed information for a specific graph."""
    graph_obj = graph_service.get_graph(name)

    if not graph_obj:
        msg = f"Graph '{name}' not found."
        raise CliException(msg)

    g = graph_obj.to_dict()

    panel_content = (
        f"[bold cyan]Name:[/] {g['name']}\n"
        f"[bold magenta]Project:[/] {g['project']}\n"
        f"[bold yellow]Status:[/] {g['status']}\n"
        f"[bold blue]Grafana:[/] {g.get('grafana', 'N/A')}"
    )
    console.print(
        Panel(panel_content, title="Graph Details", border_style="green", expand=False)
    )

    if services := g.get("services"):
        show_services(services, console)

    if hda_graph := g.get("hdaGraph"):
        yaml_content = yaml.dump(hda_graph)
        console.print(
            Panel(
                Syntax(yaml_content, "yaml", theme="monokai"),
                title="HDAG Descriptor",
                border_style="blue",
            )
        )


@graph.command()
@click.argument("name", type=click.STRING)
def remove(
    name: str, console: FromDishka[Console], graph_service: FromDishka[GraphService]
):
    """Removes a graph completely from SMO and the cluster."""
    msg = (
        f"Are you sure you want to permanently remove graph '{name}'? "
        f"This action cannot be undone."
    )
    if not click.confirm(msg, abort=True):
        return

    console.info(f"Removing graph '{name}'...")
    graph_service.remove_graph(name)
    console.success(f"Graph '{name}' removed successfully.")


@graph.command(name="re-place")
@click.argument("name", type=click.STRING)
def re_place(
    name: str, console: FromDishka[Console], graph_service: FromDishka[GraphService]
):
    """Triggers placement optimization for a deployed graph."""
    console.info(f"Triggering re-placement for graph '{name}'...")
    graph_service.trigger_placement(name)
    console.success(f"Re-placement for graph '{name}' completed successfully.")
    console.info("Check new placement with 'smo-cli graph describe'.")


@graph.command()
@click.argument("name", type=click.STRING)
def stop(
    name: str, console: FromDishka[Console], graph_service: FromDishka[GraphService]
):
    """Stops a running graph (uninstalls artifacts)."""
    msg = (
        f"Are you sure you want to stop graph '{name}'? "
        f"This will uninstall its Helm charts."
    )
    if not click.confirm(msg, abort=True):
        return

    console.info(f"Stopping graph '{name}'...")
    graph_service.stop_graph(name)
    console.success(f"Graph '{name}' stopped successfully.")


@graph.command()
@click.argument("name", type=click.STRING)
def start(
    name: str, console: FromDishka[Console], graph_service: FromDishka[GraphService]
):
    """Starts a stopped graph by reinstalling its artifacts."""
    console.info(f"Starting graph '{name}'...")
    graph_service.start_graph(name)
    console.success(f"Graph '{name}' started successfully.")


#
# Utilities
#
def get_graph_data(descriptor: str) -> dict:
    if descriptor.startswith("oci://"):
        return get_graph_from_artifact(descriptor)

    if descriptor.startswith("http://") or descriptor.startswith("https://"):
        return get_graph_from_artifact(descriptor)

    if descriptor.endswith(".yaml") or descriptor.endswith(".yml"):
        with open(descriptor, "r") as f:
            graph_data = yaml.safe_load(f)
            return graph_data

    raise ValueError(f"Invalid HDAG descriptor: {descriptor}")


def show_graphs(graphs: Iterable[Graph | dict], console: Console) -> None:
    table = Table(title="Deployed Graphs")
    table.add_column("Name", style="cyan")
    table.add_column("Project", style="magenta")
    table.add_column("Status", style="yellow")
    table.add_column("Services", style="green")
    for g_data in graphs:
        g = g_data if isinstance(g_data, dict) else g_data.to_dict()
        num_services = len(g.get("services", []))
        table.add_row(
            g["name"],
            g["project"],
            g["status"],
            str(num_services),
        )
    console.print(table)


def show_services(services: Iterable[dict], console: Console) -> None:
    table = Table(title="Services")
    table.add_column("Service Name", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Cluster Affinity", style="magenta")
    table.add_column("Artifact", style="white")
    for service in services:
        table.add_row(
            service["name"],
            service["status"],
            service.get("cluster_affinity") or "N/A",
            service["artifact_ref"],
        )
    console.print(table)

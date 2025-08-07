import typer
from fastapi.routing import APIRoute
from rich.console import Console
from rich.table import Table

from smo_ui.app import create_bare_app

cli = typer.Typer()
console = Console()


@cli.command()
def routes():
    """
    List all available routes in the SMO-UI application.
    """
    app = create_bare_app()

    table = Table(
        "[bold green]Method[/bold green]",
        "[bold green]Path[/bold green]",
        "[bold green]Name[/bold green]",
        title="[bold]SMO-UI Registered Routes[/bold]",
    )

    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(route.methods)
            table.add_row(f"[blue]{methods}[/blue]", route.path, route.name)

    console.print(table)


if __name__ == "__main__":
    cli()

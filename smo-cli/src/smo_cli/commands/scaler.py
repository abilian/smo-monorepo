import time

import click
from rich.console import Console

from smo_cli.core.context import CliContext, pass_context
from smo_core.services import scaler_service

console = Console()


@click.group()
def scaler():
    """Commands for running modular scalers."""
    pass


@scaler.command()
@click.option(
    "--target-deployment", required=True, help="Name of the deployment to scale."
)
@click.option(
    "--target-namespace", default="default", help="Namespace of the target deployment."
)
@click.option(
    "--up-threshold", type=float, required=True, help="RPS threshold to scale up."
)
@click.option(
    "--down-threshold", type=float, required=True, help="RPS threshold to scale down."
)
@click.option(
    "--up-replicas", type=int, required=True, help="Number of replicas to scale up to."
)
@click.option(
    "--down-replicas",
    type=int,
    required=True,
    help="Number of replicas to scale down to.",
)
@click.option(
    "--poll-interval", type=int, default=15, help="Seconds between scaling checks."
)
@click.option(
    "--cooldown-period",
    type=int,
    default=60,
    help="Seconds to wait after a scaling action.",
)
@pass_context
def run(
    ctx: CliContext,
    target_deployment: str,
    target_namespace: str,
    up_threshold: float,
    down_threshold: float,
    up_replicas: int,
    down_replicas: int,
    poll_interval: int,
    cooldown_period: int,
):
    """Run the threshold-based autoscaler in a continuous loop."""
    console.print("H3NI Modular Scaler (via SMO-CLI) Starting", style="bold green")
    console.print(f"  - Target: [cyan]{target_namespace}/{target_deployment}[/cyan]")
    console.print(
        f"  - Scale Up: > [bold magenta]{up_threshold}[/bold magenta] RPS -> [bold green]{up_replicas}[/bold green] replicas"
    )
    console.print(
        f"  - Scale Down: < [bold magenta]{down_threshold}[/bold magenta] RPS -> [bold red]{down_replicas}[/bold red] replicas"
    )
    console.print(
        f"  - Timings: Poll every {poll_interval}s, Cooldown {cooldown_period}s"
    )
    console.print("-" * 50)

    last_scale_time = 0

    while True:
        now = time.time()
        if (now - last_scale_time) < cooldown_period:
            console.print(
                f"In cooldown period. Waiting for {cooldown_period - (now - last_scale_time):.0f} more seconds.",
                style="dim",
            )
        else:
            # Ensure context is active if needed, though this service doesn't use DB
            with ctx.db_session():
                result = scaler_service.run_threshold_scaler_iteration(
                    karmada=ctx.core_context.karmada,
                    prometheus=ctx.core_context.prometheus,
                    target_deployment=target_deployment,
                    target_namespace=target_namespace,
                    scale_up_threshold=up_threshold,
                    scale_down_threshold=down_threshold,
                    scale_up_replicas=up_replicas,
                    scale_down_replicas=down_replicas,
                )

            action = result.get("action")
            if action in ("scale_up", "scale_down"):
                console.print(
                    f"[bold green]SCALING ACTION TAKEN:[/] {result['reason']}"
                )
                last_scale_time = time.time()
            elif action == "none":
                console.print(
                    f"No action needed. Replicas: {result.get('current_replicas')}, Rate: {result.get('request_rate', 0):.2f} RPS"
                )
            else:  # error
                console.print(
                    f"[bold red]Error in scaling iteration:[/] {result.get('reason')}"
                )

        time.sleep(poll_interval)

from dataclasses import dataclass
from functools import update_wrapper
from typing import Callable

import click
from rich.console import Console

from smo_core.context import SmoContext
from smo_core.utils.grafana_helper import GrafanaHelper
from smo_core.utils.karmada_helper import KarmadaHelper
from smo_core.utils.prometheus_helper import PrometheusHelper

from .config import get_config
from .database import SessionLocal

console = Console()


@dataclass
class CliContext:
    """
    A CLI-specific context object that initializes and holds state.
    It creates a SmoContext instance from smo-core to pass to service functions.
    """

    cli_config: dict

    _db_session_factory: Callable = SessionLocal

    # Lazy-loaded helpers
    _karmada_helper: KarmadaHelper = None
    _prometheus_helper: PrometheusHelper = None
    _grafana_helper: GrafanaHelper = None
    _smo_context: SmoContext = None

    def db_session(self):
        """Provides a new database session."""
        return self._db_session_factory()

    @property
    def karmada(self) -> KarmadaHelper:
        if self._karmada_helper is None:
            self._karmada_helper = KarmadaHelper(self.cli_config["karmada_kubeconfig"])
        return self._karmada_helper

    @property
    def prometheus(self) -> PrometheusHelper:
        if self._prometheus_helper is None:
            self._prometheus_helper = PrometheusHelper(
                self.cli_config["prometheus_host"],
                time_window=str(self.cli_config["scaling"]["interval_seconds"]),
            )
        return self._prometheus_helper

    @property
    def grafana(self) -> GrafanaHelper:
        if self._grafana_helper is None:
            self._grafana_helper = GrafanaHelper(
                self.cli_config["grafana"]["host"],
                self.cli_config["grafana"]["username"],
                self.cli_config["grafana"]["password"],
            )
        return self._grafana_helper

    @property
    def core_context(self) -> SmoContext:
        """Creates and returns the shared SmoContext object for the service layer."""
        if self._smo_context is None:
            self._smo_context = SmoContext(
                config=self.cli_config,
                karmada=self.karmada,
                prometheus=self.prometheus,
                grafana=self.grafana,
            )
        return self._smo_context


def pass_context(f):
    """A custom decorator that passes the CliContext object to the command."""

    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        cli_ctx = get_context()
        return ctx.invoke(f, cli_ctx, *args, **kwargs)

    return update_wrapper(new_func, f)


_cli_context: CliContext | None = None


def get_context() -> CliContext:
    """
    Initializes the CLI context object and handles any exceptions that may occur.
    """
    global _cli_context

    if _cli_context is not None:
        return _cli_context

    try:
        # The context object is created once and passed down.
        cli_config = get_config()
    except FileNotFoundError as e:
        # Handle case where config file is missing for non-init commands
        console.print(f"[bold red]Error:[/] {e}")
        console.print(
            "Please run 'smo-cli init' to create the configuration file.",
            style="yellow",
        )
        exit(1)

    try:
        ctx = CliContext(cli_config)
    except Exception as e:
        console.print(
            f"[bold red]An unexpected error occurred during initialization:[/] {e}"
        )
        exit(1)
    _cli_context = ctx
    return ctx

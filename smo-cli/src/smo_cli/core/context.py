from dataclasses import dataclass
from functools import update_wrapper

import click
from rich.console import Console

from smo_core.context import SmoContext
from smo_core.helpers import GrafanaHelper
from smo_core.helpers import KarmadaHelper
from smo_core.helpers import PrometheusHelper

from .config import Config

console = Console()


@dataclass
class CliContext:
    """
    A CLI-specific context object that initializes and holds state.
    It creates a SmoContext instance from smo-core to pass to service functions.
    """

    cli_config: Config

    # Lazy-loaded helpers
    _karmada_helper: KarmadaHelper = None
    _prometheus_helper: PrometheusHelper = None
    _grafana_helper: GrafanaHelper = None
    _smo_context: SmoContext = None

    @property
    def config_data(self):
        """Returns the CLI configuration data."""
        return self.cli_config.data

    def db_session(self):
        """Provides a new database session."""
        from smo_cli.core.database import DbManager

        db_manager = DbManager(self.cli_config)
        session_factory = db_manager.get_session_factory()
        return session_factory()

    @property
    def karmada(self) -> KarmadaHelper:
        if self._karmada_helper is None:
            self._karmada_helper = KarmadaHelper(self.config_data["karmada_kubeconfig"])
        return self._karmada_helper

    @property
    def prometheus(self) -> PrometheusHelper:
        if self._prometheus_helper is None:
            self._prometheus_helper = PrometheusHelper(
                self.config_data["prometheus_host"],
                time_window=str(self.config_data["scaling"]["interval_seconds"]),
            )
        return self._prometheus_helper

    @property
    def grafana(self) -> GrafanaHelper:
        if self._grafana_helper is None:
            self._grafana_helper = GrafanaHelper(
                self.config_data["grafana"]["host"],
                self.config_data["grafana"]["username"],
                self.config_data["grafana"]["password"],
            )
        return self._grafana_helper

    @property
    def core_context(self) -> SmoContext:
        """Creates and returns the shared SmoContext object for the service layer."""
        if self._smo_context is None:
            self._smo_context = SmoContext(
                config=self.config_data,
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
        cli_config = Config.load()
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

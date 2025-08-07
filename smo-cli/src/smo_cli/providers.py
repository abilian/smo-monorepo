"""
This module contains the Dishka Providers for the SMO-CLI application.

Providers instruct the DI container how to create and manage the lifecycle of our application's services and components.
"""

from collections.abc import Iterable

import click
from dishka import Provider, Scope, from_context, provide
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

# --- Core Helpers and Services ---
from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper
from smo_core.services import ClusterService, GraphService, ScalerService

# --- Core Application Components ---
from .config import Config
from .console import Console


class ConfigProvider(Provider):
    """Provides the main configuration object, loaded once per application run."""

    scope = Scope.APP

    @provide
    def get_config(self) -> Config:
        """Loads the config from ~/.smo/config.yaml"""
        try:
            return Config.load()
        except FileNotFoundError as e:
            print(f"[bold red]Error:[/] {e}")
            print("Please run 'smo-cli init' to create the configuration file.")
            raise click.Abort()


class ConsoleProvider(Provider):
    """Provides our custom console, respecting the verbosity level."""

    scope = Scope.APP
    verbosity = from_context(provides=int, scope=Scope.APP)

    @provide
    def get_console(self, verbosity: int) -> Console:
        """Creates a single console instance based on the verbosity flag."""
        return Console(verbosity=verbosity)


class DbProvider(Provider):
    """Manages the database connection lifecycle."""

    scope = Scope.APP

    @provide
    def get_db_engine(self, config: Config) -> Engine:
        db_url = config.get("db.url")
        return create_engine(db_url)

    @provide
    def get_db_session(self, engine: Engine) -> Iterable[Session]:
        """Provides a SQLAlchemy session that is automatically closed after use."""
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = session_factory()
        try:
            yield session
        finally:
            session.close()


class InfraProvider(Provider):
    """Provides helpers for interacting with external systems like Karmada."""

    scope = Scope.APP

    @provide
    def get_karmada(self, config: Config, console: Console) -> KarmadaHelper:
        console.debug("Initializing KarmadaHelper...")
        return KarmadaHelper(config.get("karmada_kubeconfig"))

    @provide
    def get_prometheus(self, config: Config, console: Console) -> PrometheusHelper:
        console.debug("Initializing PrometheusHelper...")
        return PrometheusHelper(
            config.get("prometheus_host"),
            time_window=str(config.get("scaling.interval_seconds")),
        )

    @provide
    def get_grafana(self, config: Config, console: Console) -> GrafanaHelper:
        console.debug("Initializing GrafanaHelper...")
        return GrafanaHelper(
            config.get("grafana.host"),
            config.get("grafana.username"),
            config.get("grafana.password"),
        )


class ServiceProvider(Provider):
    """Provides the core business logic services."""

    scope = Scope.APP

    @provide
    def get_cluster_service(
        self,
        session: Session,
        karmada: KarmadaHelper,
        grafana: GrafanaHelper,
        config: Config,
    ) -> ClusterService:
        return ClusterService(
            db_session=session,
            karmada_helper=karmada,
            grafana_helper=grafana,
            config=config.data,
        )

    @provide
    def get_graph_service(
        self,
        session: Session,
        karmada: KarmadaHelper,
        grafana: GrafanaHelper,
        prometheus: PrometheusHelper,
        config: Config,
    ) -> GraphService:
        return GraphService(
            db_session=session,
            karmada_helper=karmada,
            grafana_helper=grafana,
            prom_helper=prometheus,
            config=config.data,
        )

    @provide
    def get_scaler_service(
        self, karmada: KarmadaHelper, prometheus: PrometheusHelper
    ) -> ScalerService:
        return ScalerService(karmada=karmada, prometheus=prometheus)


main_providers = [
    ConfigProvider(),
    ConsoleProvider(),
    DbProvider(),
    InfraProvider(),
    ServiceProvider(),
]

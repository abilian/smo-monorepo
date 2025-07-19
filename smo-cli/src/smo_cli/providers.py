#
# WARNING: not used yet!
#

from typing import Iterator

from dishka import Provider, Scope, provide
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session, sessionmaker

from smo_core.helpers import PrometheusHelper
from smo_core.helpers.grafana.grafana_helper import GrafanaHelper
from smo_core.helpers.karmada_helper import KarmadaHelper
from smo_core.models.base import Base


class Config:
    @staticmethod
    def load():
        return Config()

    @property
    def db_file(self):
        return "smo_cli.db"


class ConfigProvider(Provider):
    """Provides the main configuration object."""

    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        """Loads config from the default path. Fails if not found."""
        try:
            # The init command must be run before any other command.
            return Config.load()
        except FileNotFoundError as e:
            print("ERROR: Configuration not found. Please run `smo-cli init` first.")
            raise e


class InfraProvider(Provider):
    """Provides infrastructure helper clients."""

    # All helpers are singletons for the app's lifetime
    scope = Scope.APP

    grafana = provide(GrafanaHelper)
    prometheus = provide(PrometheusHelper)
    karmada = provide(KarmadaHelper)


class DbProvider(Provider):
    """Provides the database session."""

    @provide(scope=Scope.APP)
    def get_engine(self, config: Config) -> Engine:
        """Creates the SQLAlchemy engine once per application run."""
        db_uri = f"sqlite:///{config.db_file}"
        engine = create_engine(db_uri)
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        return engine

    @provide(scope=Scope.APP)
    def get_session(self, engine: Engine) -> Iterator[Session]:
        """
        Provides a database session that is properly closed after use.
        This is a generator-based factory.
        """
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        try:
            yield session
        finally:
            session.close()


# Combine all providers for easy use in the container
main_providers = [ConfigProvider(), InfraProvider(), DbProvider()]

from collections.abc import Iterable

from devtools import debug
from dishka import Provider, Scope, provide
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from smo_core.context import SmoCoreContext
from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper
from smo_core.models.base import Base
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_core.services.scaler_service import ScalerService
from smo_ui.config import Config

CONFIG = {
    "grafana": {
        "host": "http://localhost:3000",
        "password": "admin",
        "username": "admin",
    },
    "helm": {"insecure_registry": True},
    "karmada_kubeconfig": "/Users/fermigier/.kube/karmada-apiserver.config",
    "prometheus_host": "http://localhost:9090",
    "scaling": {"interval_seconds": 30},
    "smo_dir": "/Users/fermigier/.smo",
}


class ConfigProvider(Provider):
    """Provides configuration from config.yaml"""

    scope = Scope.APP

    @provide
    def get_config(self) -> Config:
        config_data = CONFIG
        debug(config_data)
        config_data["db_file"] = "data/smo.db"
        return Config(config_data)


class DbProvider(Provider):
    """Manages the database connection lifecycle."""

    @provide(scope=Scope.APP)
    def get_db_engine(self, config: Config) -> Engine:
        db_file = config.data["db_file"]
        engine = create_engine(f"sqlite:///{db_file}")
        Base.metadata.create_all(engine)
        return engine

    @provide(scope=Scope.REQUEST)
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

    scope = Scope.REQUEST

    @provide
    def get_karmada(self, config: Config) -> KarmadaHelper:
        return KarmadaHelper(config.get("karmada_kubeconfig"))

    @provide
    def get_prometheus(self, config: Config) -> PrometheusHelper:
        return PrometheusHelper(
            config.get("prometheus_host"),
            time_window=str(config.get("scaling.interval_seconds")),
        )

    @provide
    def get_grafana(self, config: Config) -> GrafanaHelper:
        return GrafanaHelper(
            config.get("grafana.host"),
            config.get("grafana.username"),
            config.get("grafana.password"),
        )


class ServiceProvider(Provider):
    """Provides the core business logic services."""

    scope = Scope.REQUEST

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
        self,
        karmada: KarmadaHelper,
        prometheus: PrometheusHelper,
    ) -> ScalerService:
        return ScalerService(karmada=karmada, prometheus=prometheus)


class ContextProvider(Provider):
    """Provides SmoCoreContext"""

    scope = Scope.REQUEST

    @provide
    def get_context(
        self,
        config: Config,
        karmada: KarmadaHelper,
        prometheus: PrometheusHelper,
        grafana: GrafanaHelper,
    ) -> SmoCoreContext:
        return SmoCoreContext(
            config=config.data,
            karmada=karmada,
            prometheus=prometheus,
            grafana=grafana,
        )


# main_providers = [
#     ConfigProvider(),
#     ConsoleProvider(),
#     DbProvider(),
#     InfraProvider(),
#     ServiceProvider(),
# ]
main_providers = [
    DbProvider(),
    ConfigProvider(),
    ContextProvider(),
    InfraProvider(),
    ServiceProvider(),
]

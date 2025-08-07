import os
from collections.abc import Iterable
from pathlib import Path

from dishka import Provider, Scope, provide
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper
from smo_core.models.base import Base
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_core.services.scaler_service import ScalerService
from smo_ui.config import Config

SMO_DIR = Path(os.getenv("SMO_DIR", "~/.smo")).expanduser()
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
    "db": {
        "url": f"sqlite:///{SMO_DIR}/smo.db",
    },
    "smo_dir": str(SMO_DIR),
}


class ConfigProvider(Provider):
    """Provides configuration from config.yaml"""

    @provide(scope=Scope.REQUEST)
    def get_config(self) -> Config:
        return Config(CONFIG)


class DbProvider(Provider):
    """Manages the database connection lifecycle."""

    @provide(scope=Scope.REQUEST)
    def get_db_engine(self, config: Config) -> Engine:
        engine = create_engine(config.get("db.url"))
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


main_providers = [
    DbProvider(),
    ConfigProvider(),
    InfraProvider(),
    ServiceProvider(),
]

from smo_core.context import SmoCoreContext
from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper

from .config import config
from .database import DbManager


def get_core_context() -> SmoCoreContext:
    """Creates the core context object needed by service functions for a request."""
    core_config = config["SMO_CORE_CONFIG"]
    grafana_config = core_config["grafana"]
    return SmoCoreContext(
        config=core_config,
        karmada=KarmadaHelper(core_config["karmada_kubeconfig"]),
        prometheus=PrometheusHelper(core_config["prometheus_host"]),
        grafana=GrafanaHelper(
            grafana_config["host"],
            grafana_config["username"],
            grafana_config["password"],
        ),
    )


def get_db_session():
    """Returns the request-scoped database session."""

    db_manager = DbManager(config)
    session_factory = db_manager.get_session_factory()
    return session_factory()

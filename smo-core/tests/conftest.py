# tests/conftest.py
import os
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_core.context import SmoContext
from smo_core.database import Base
from smo_core.utils.helpers import format_memory

# Hack for MacOS
os.environ["PATH"] = "/opt/homebrew/bin:" + os.environ.get("PATH", "")


# --- Mock Helper Classes ---


class MockKarmadaHelper:
    """Mock class for KarmadaHelper to simulate Karmada interactions in tests."""

    def __init__(self, *args, **kwargs):
        self.deployments = {
            "test-vo": {"replicas": 1, "cpu_limit": 0.5},
            "test-service": {"replicas": 1, "cpu_limit": 1.0},
        }

    def get_cluster_info(self):
        return {
            "cluster-1": {
                "total_cpu": 16.0,
                "allocated_cpu": 4.0,
                "remaining_cpu": 12.0,
                "total_memory_bytes": format_memory(64 * 1024**3),
                "allocated_memory_bytes": format_memory(16 * 1024**3),
                "remaining_memory_bytes": format_memory(48 * 1024**3),
                "availability": True,
            },
            "cluster-2": {
                "total_cpu": 32.0,
                "allocated_cpu": 10.0,
                "remaining_cpu": 22.0,
                "total_memory_bytes": format_memory(128 * 1024**3),
                "allocated_memory_bytes": format_memory(30 * 1024**3),
                "remaining_memory_bytes": format_memory(98 * 1024**3),
                "availability": False,
            },
        }

    def get_replicas(self, name):
        return self.deployments.get(name, {}).get("replicas", 0)

    def get_cpu_limit(self, name):
        return self.deployments.get(name, {}).get("cpu_limit", 0)

    def scale_deployment(self, name, replicas):
        if name in self.deployments:
            self.deployments[name]["replicas"] = replicas
        print(f"MOCK SCALE: Scaled {name} to {replicas} replicas.")


class MockPrometheusHelper:
    """Mock class for PrometheusHelper."""

    def __init__(self, *args, **kwargs):
        self.update_alert_rules = MagicMock()

    def get_request_rate(self, name):
        return 10.0

    # update_alert_rules is a MagicMock, so we can assert calls on it


class MockGrafanaHelper:
    """Mock class for GrafanaHelper."""

    def __init__(self, *args, **kwargs):
        pass

    def publish_dashboard(self, dashboard_json):
        uid = dashboard_json.get("dashboard", {}).get("uid", "test-uid")
        return {"url": f"/d/{uid}/test-dashboard"}

    def create_cluster_dashboard(self, cluster_name):
        return {"dashboard": {"uid": cluster_name}}

    def create_graph_dashboard(self, graph_name, service_names):
        return {"dashboard": {"uid": graph_name}}

    def create_graph_service(self, service_name):
        return {"dashboard": {"uid": service_name}}


# --- Pytest Fixtures ---


@pytest.fixture(scope="function")
def db_session():
    """Provides a transactional scope around a test function with an in-memory SQLite DB."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def mock_context(mocker):
    """Provides a fully mocked SmoContext object."""
    mock_config = {
        "karmada_kubeconfig": "/tmp/fake-karmada.config",
        "grafana": {
            "host": "http://mock-grafana",
            "username": "admin",
            "password": "password",
        },
        "prometheus_host": "http://mock-prometheus",
        "helm": {"insecure_registry": True},
        "scaling": {"interval_seconds": 30},
    }

    # Mock external command execution to avoid real subprocess calls
    mocker.patch(
        "smo_core.utils.external_commands.run_hdarctl",
        return_value="Mock hdarctl output",
    )
    mocker.patch(
        "smo_core.utils.external_commands.run_helm", return_value="Mock helm output"
    )

    context = SmoContext(
        config=mock_config,
        karmada=MockKarmadaHelper(),
        prometheus=MockPrometheusHelper(),
        grafana=MockGrafanaHelper(),
    )
    return context

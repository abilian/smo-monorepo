import os
from pathlib import Path
from textwrap import dedent
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from dishka import Container, Provider, Scope, make_container, provide

from smo_cli.cli import main
from smo_cli.providers import (
    ConfigProvider,
    ConsoleProvider,
    DbProvider,
    InfraProvider,
)
from smo_core.models.graph import Graph
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_core.services.scaler_service import ScalerService


#
# --- MOCK SERVICE IMPLEMENTATIONS ---
#
class MockClusterService:
    def fetch_clusters(self) -> list[dict]:
        return [
            {
                "name": "cluster-1",
                "availability": True,
                "location": "us-east-1",
                "acceleration": True,
                "available_cpu": 12.0,
                "available_ram": "48.00 GiB",
            },
            {
                "name": "cluster-2",
                "availability": False,
                "location": "eu-west-1",
                "acceleration": False,
                "available_cpu": 20.0,
                "available_ram": "90.00 GiB",
            },
        ]

    def list_clusters(self) -> list[dict]:
        return self.fetch_clusters()


class MockGraphService:
    def __init__(self):
        self.deploy_graph = MagicMock()
        self.remove_graph = MagicMock()
        self.trigger_placement = MagicMock()
        self.start_graph = MagicMock()
        self.stop_graph = MagicMock()

        self.db_session = MagicMock()
        self.db_session.query.return_value.all.return_value = [
            Graph(name="db-graph", project="db-proj", status="Running", services=[])
        ]

    def fetch_project_graphs(self, project: str) -> list[dict]:
        if project == "empty-project":
            return []
        return [
            {
                "name": f"{project}-graph-1",
                "project": project,
                "status": "Running",
                "services": [],
            },
            {
                "name": f"{project}-graph-2",
                "project": project,
                "status": "Stopped",
                "services": [],
            },
        ]

    def fetch_graph(self, name: str) -> MagicMock | None:
        if name == "non-existent-graph":
            return None

        mock_graph_obj = MagicMock(spec=Graph)
        mock_graph_obj.to_dict.return_value = {
            "name": name,
            "project": "default",
            "status": "Running",
            "services": [],
            "grafana": None,
            "hdaGraph": {"id": name, "version": "1.0.0"},
            "placement": {},
        }
        return mock_graph_obj


class MockScalerService:
    def run_threshold_scaler_iteration(self, **kwargs):
        return {
            "action": "scale_up",
            "new_replicas": 3,
            "reason": "Mocked scaling action.",
            "current_replicas": 2,
        }


#
# --- MOCK DISHKA PROVIDER ---
#
class MockServiceProvider(Provider):
    # ... (no changes, this is correct)
    scope = Scope.APP

    @provide(provides=ClusterService)
    def get_mock_cluster_service(self) -> MockClusterService:
        return MockClusterService()

    @provide(provides=GraphService)
    def get_mock_graph_service(self) -> MockGraphService:
        if not hasattr(self, "_mock_graph_service"):
            self._mock_graph_service = MockGraphService()
        return self._mock_graph_service

    @provide(provides=ScalerService)
    def get_mock_scaler_service(self) -> MockScalerService:
        return MockScalerService()


#
# --- PYTEST FIXTURES ---
#
@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="function")
def tmp_smo_dir(tmp_path: Path, runner: CliRunner) -> Path:
    smo_dir = tmp_path / ".smo"
    os.environ["SMO_DIR"] = str(smo_dir)
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0, f"smo-cli init failed: {result.output}"
    return smo_dir


@pytest.fixture
def dishka_container(tmp_smo_dir: Path) -> Generator[Container, Any, None]:
    container = make_container(
        ConfigProvider(),
        DbProvider(),
        InfraProvider(),
        ConsoleProvider(),
        MockServiceProvider(),
        context={int: 0},
    )
    yield container
    container.close()


@pytest.fixture
def client(runner: CliRunner, dishka_container: Container, mocker) -> CliRunner:
    mocker.patch("smo_cli.cli.make_container", return_value=dishka_container)
    return runner


@pytest.fixture
def mock_graph_service(dishka_container: Container) -> MockGraphService:
    return dishka_container.get(GraphService)


@pytest.fixture
def mock_cluster_service(dishka_container: Container) -> MockClusterService:
    return dishka_container.get(ClusterService)


@pytest.fixture
def hdag_file(tmp_path: Path) -> str:
    hdag_content = dedent("""
        hdaGraph:
          id: my-test-graph
          services:
            - id: service-a
              deployment:
                trigger: { auto: {} }
                intent:
                  compute: { cpu: "light", ram: "light", storage: "small", gpu: { enabled: false } }
              artifact:
                ociImage: "oci://example.com/service-a"
                ociConfig: { type: App, implementer: HELM }
                valuesOverwrite: {}
    """)
    f = tmp_path / "hdag.yaml"
    f.write_text(hdag_content)
    return str(f)

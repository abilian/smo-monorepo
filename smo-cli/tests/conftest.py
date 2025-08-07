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
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService


#
# --- MOCK SERVICE IMPLEMENTATIONS ---
#
class MockClusterService:
    """A mock implementation of the ClusterService for testing."""

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
    """A mock implementation of the GraphService for testing."""

    def __init__(self):
        # Using MagicMock allows us to assert if these methods were called
        self.deploy_graph = MagicMock()
        self.remove_graph = MagicMock()
        self.trigger_placement = MagicMock()
        self.start_graph = MagicMock()
        self.stop_graph = MagicMock()

    def fetch_project_graphs(self, project: str) -> list[dict]:
        if project == "empty-project":
            return []
        # Return a list of dicts that look like the .to_dict() output of the model
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

    def fetch_graph(self, name: str) -> dict | None:
        if name == "non-existent-graph":
            return None
        # Return a dict that can be converted by .to_dict() in the command
        return {
            "name": name,
            "project": "default",
            "status": "Running",
            "services": [],
            "grafana": None,
            "hdaGraph": {"id": name, "version": "1.0.0"},
            "placement": {},
        }


#
# --- MOCK DISHKA PROVIDER ---
#
class MockServiceProvider(Provider):
    """
    This provider overrides the real ServiceProvider. Instead of creating
    real services, it provides our mock implementations.
    """

    scope = Scope.APP

    @provide(provides=ClusterService)
    def get_mock_cluster_service(self) -> MockClusterService:
        return MockClusterService()

    @provide(provides=GraphService)
    def get_mock_graph_service(self) -> MockGraphService:
        # Return a singleton instance so we can inspect its MagicMocks
        if not hasattr(self, "_mock_graph_service"):
            self._mock_graph_service = MockGraphService()
        return self._mock_graph_service


#
# --- PYTEST FIXTURES ---
#
@pytest.fixture
def runner() -> CliRunner:
    """Provides a basic Click CliRunner."""
    return CliRunner()


@pytest.fixture(scope="function")
def tmp_smo_dir(tmp_path: Path, runner: CliRunner) -> Path:
    """
    Creates a temporary ~/.smo directory and runs `smo-cli init`.
    """
    smo_dir = tmp_path / ".smo"
    os.environ["SMO_DIR"] = str(smo_dir)
    result = runner.invoke(main, ["init"])
    assert result.exit_code == 0, f"smo-cli init failed: {result.output}"
    return smo_dir


@pytest.fixture
def dishka_container(tmp_smo_dir: Path) -> Generator[Container, Any, None]:
    """
    Creates a SYNCHRONOUS dishka container configured for testing.
    """
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
    """
    Patches the CLI's entrypoint to use our pre-configured mock container.
    """
    mocker.patch("smo_cli.cli.make_container", return_value=dishka_container)
    return runner


@pytest.fixture
def mock_graph_service(dishka_container: Container) -> MockGraphService:
    """
    Gets the singleton instance of our MockGraphService from the test container.
    """
    return dishka_container.get(GraphService)


@pytest.fixture
def hdag_file(tmp_path: Path) -> str:
    """Creates a temporary, structurally valid HDAG YAML file."""
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

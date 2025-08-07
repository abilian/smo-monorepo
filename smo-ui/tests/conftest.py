from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from dishka import Provider, Scope, make_async_container, provide
from fastapi.testclient import TestClient

from smo_core.models import Graph
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_ui.app import create_app
from smo_ui.providers import ConfigProvider


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
                "grafana": "http://grafana.test/d/cluster-1",
            },
            {
                "name": "cluster-2",
                "availability": False,
                "location": "eu-west-1",
                "acceleration": False,
                "available_cpu": 20.0,
                "available_ram": "90.00 GiB",
                "grafana": "http://grafana.test/d/cluster-2",
            },
        ]

    def list_clusters(self) -> list:
        return self.fetch_clusters()


class MockGraphService:
    def __init__(self):
        self.deploy_graph = MagicMock()

    def get_graphs(self, project: str = "") -> list[Graph]:
        return [
            Graph(name="graph-1", project="default", status="Running"),
            Graph(name="graph-2", project="default", status="Stopped"),
        ]

    def get_graph(self, name: str) -> Graph | None:
        if name == "graph-1":
            return Graph(
                name="graph-1",
                project="default",
                status="Running",
                graph_descriptor={"id": "graph-1", "version": "1.0.0"},
                services=[MagicMock(name="service-a")],
            )
        return None

    def get_graph_from_artifact(self, url: str) -> dict:
        return {"id": "graph-from-oci", "hdaGraph": {"id": "graph-from-oci"}}


@pytest.fixture
def mock_graph_service() -> MockGraphService:
    """Fixture to provide an instance of the mock graph service."""
    return MockGraphService()


@pytest.fixture
def mock_cluster_service() -> MockClusterService:
    """Fixture to provide an instance of the mock cluster service."""
    return MockClusterService()


@pytest.fixture
def client(
    mock_graph_service: MockGraphService, mock_cluster_service: MockClusterService
) -> Generator[TestClient]:
    """
    Main fixture for API tests. Creates a clean FastAPI app for each test,
    with a DI container providing the specified mock services.
    """

    class TestProvider(Provider):
        scope = Scope.APP

        @provide
        def get_graph_service(self) -> GraphService:
            return mock_graph_service

        @provide
        def get_cluster_service(self) -> ClusterService:
            return MockClusterService()

    container = make_async_container(TestProvider(), ConfigProvider())

    app = create_app(container=container)

    # TestClient handles the app lifespan, including startup/shutdown of the container
    with TestClient(app) as test_client:
        yield test_client

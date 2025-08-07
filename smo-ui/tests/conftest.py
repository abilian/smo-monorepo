from collections.abc import AsyncIterator
from unittest.mock import MagicMock

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi.testclient import TestClient

from smo_core.models import Graph
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_ui.app import create_app


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

    def get_graphs(self, project: str="") -> list[Graph]:
        return [
            Graph(name="graph-1", project="default", status="Running", services=[]),
            Graph(name="graph-2", project="default", status="Stopped", services=[]),
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


class MockGraphProvider(Provider):
    scope = Scope.REQUEST
    service = provide(MockGraphService, provides=GraphService)


class MockClusterProvider(Provider):
    scope = Scope.REQUEST
    service = provide(MockClusterService, provides=ClusterService)


@pytest.fixture
def mock_graph_service(dishka_container: AsyncContainer) -> MockGraphService:
    return dishka_container.get_sync(GraphService)


@pytest.fixture
async def dishka_container() -> AsyncIterator[AsyncContainer]:
    container = make_async_container(
        MockGraphProvider(),
        MockClusterProvider(),
    )
    yield container
    await container.close()


@pytest.fixture
def client(dishka_container: AsyncContainer) -> TestClient:
    app = create_app()
    setup_dishka(container=dishka_container, app=app)
    return TestClient(app)


#
# Pre-dishka code for reference, not used in the current setup.
#

# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
#
# from smo_core.models import Cluster, Graph, Service
# from smo_core.models.base import Base
# from smo_ui.app import app
# from smo_ui.extensions import get_db
#
# assert Cluster and Graph and Service
#
# # Setup test database
# TEST_DATABASE_URL = "sqlite:///:memory:"
# engine = create_engine(
#     TEST_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     echo=True,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
# # Create tables once at module level
# Base.metadata.create_all(bind=engine)
#
#
# # Not used yet.
# class MockKarmadaHelper:
#     """Mock Karmada helper for testing"""
#
#     def get_cluster_info(self):
#         return []
#
#     def get_replicas(self, name):
#         return 1
#
#     def get_cpu_limit(self, name):
#         return 1.0
#
#     def scale_deployment(self, name, replicas):
#         pass
#
#
# @pytest.fixture
# def db_session():
#     """Fixture to provide a test database session"""
#     # Create all tables fresh for each test
#     Base.metadata.create_all(bind=engine)
#
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.rollback()
#         db.close()
#
#
# @pytest.fixture
# def client(db_session):
#     """Fixture to provide a test client with overridden dependencies"""
#
#     def override_get_db():
#         try:
#             yield db_session
#         finally:
#             db_session.close()
#
#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as test_client:
#         yield test_client
#     app.dependency_overrides.clear()
#
#
# @pytest.fixture(autouse=True)
# def clean_db(db_session):
#     """Clean database after each test"""
#     yield
#     # Clear all data but keep tables
#     for table in reversed(Base.metadata.sorted_tables):
#         db_session.execute(table.delete())
#     db_session.commit()

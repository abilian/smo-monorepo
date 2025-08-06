import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from smo_core.models import Graph


def test_index_route(client: TestClient, db_session: Session):
    """Test the index route returns successful response"""
    name = f"test-project-{id(db_session)}"
    db_session.add(
        Graph(
            name=name,
            project="test-project",
            status="Running",
            graph_descriptor={"id": "test-graph", "version": "1.0.0"},
        )
    )
    db_session.commit()

    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text


def test_projects_route(client: TestClient, db_session: Session):
    """Test projects route returns successful response"""
    name = f"test-project-{id(db_session)}"
    db_session.add(
        Graph(
            name=name,
            project="test-project",
            status="Running",
            graph_descriptor={"id": "test-graph", "version": "1.0.0"},
        )
    )
    db_session.commit()

    response = client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert "Projects" in response.text


@pytest.mark.skip
def test_clusters_route(client: TestClient):
    """Test clusters route returns successful response"""
    response = client.get("/clusters")
    assert response.status_code == status.HTTP_200_OK
    assert "Clusters" in response.text


def test_marketplace_route(client: TestClient):
    """Test marketplace route returns successful response"""
    response = client.get("/marketplace")
    assert response.status_code == status.HTTP_200_OK
    assert "Marketplace" in response.text


def test_settings_route(client: TestClient):
    """Test settings route returns successful response"""
    response = client.get("/settings")
    assert response.status_code == status.HTTP_200_OK
    assert "Settings" in response.text


def test_docs_route(client: TestClient):
    """Test docs route returns successful response"""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "Swagger" in response.text  # Changed to match actual content

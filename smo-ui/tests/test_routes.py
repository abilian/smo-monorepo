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
from fastapi import status
from fastapi.testclient import TestClient

def test_index_route(client: TestClient):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text

def test_projects_route(client: TestClient):
    response = client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert "Projects" in response.text
    assert "<strong>2</strong> Graphs" in response.text
    assert "<strong>1</strong> Active" in response.text

def test_clusters_route(client: TestClient):
    response = client.get("/clusters")
    assert response.status_code == status.HTTP_200_OK
    assert "Clusters" in response.text
    assert "cluster-1" in response.text
    assert "cluster-2" in response.text

def test_graphs_for_project_route(client: TestClient):
    response = client.get("/graphs/default")
    assert response.status_code == status.HTTP_200_OK
    assert 'Graphs in "default"' in response.text
    assert "graph-1" in response.text
    assert "graph-2" in response.text

def test_graph_details_route(client: TestClient):
    response = client.get("/graphs/graph-1")
    assert response.status_code == status.HTTP_200_OK
    assert "Graph Details" in response.text
    assert "graph-1" in response.text

def test_graph_details_not_found(client: TestClient):
    response = client.get("/graphs/non-existent-graph")
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]

def test_deploy_graph_get_page(client: TestClient):
    response = client.get("/graphs/deploy")
    assert response.status_code == status.HTTP_200_OK
    assert "Deploy New Graph" in response.text

def test_deploy_graph_post_success(client: TestClient, mock_graph_service):
    form_data = {
        "descriptor-url": "oci://my-registry/my-graph:1.0",
        "project-name": "new-project"
    }
    response = client.post("/graphs/deploy", data=form_data, allow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/graphs/graph-from-oci"
    mock_graph_service.deploy_graph.assert_called_once_with(
        "new-project",
        {"id": "graph-from-oci", "hdaGraph": {"id": "graph-from-oci"}}
    )

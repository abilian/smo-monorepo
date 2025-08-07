# File: tests/test_routes.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient

# Import mock service for type hinting in test function signatures
from .conftest import MockGraphService


def test_index_route(client: TestClient):
    """Tests the main dashboard route."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "Dashboard" in response.text


def test_projects_route(client: TestClient):
    """Tests the projects overview page."""
    response = client.get("/projects")
    assert response.status_code == status.HTTP_200_OK
    assert "Projects" in response.text
    # Assertions based on mock data from MockGraphService
    assert "<strong>2</strong> Graphs" in response.text
    assert "<strong>1</strong> Active" in response.text


def test_clusters_route(client: TestClient):
    """Tests the federated clusters page."""
    response = client.get("/clusters")
    assert response.status_code == status.HTTP_200_OK
    assert "Clusters" in response.text
    # Assertions based on mock data from MockClusterService
    assert "cluster-1" in response.text
    assert "cluster-2" in response.text


def test_graphs_for_project_route(client: TestClient):
    """Tests the page listing graphs for a specific project."""
    response = client.get("/graphs/default")
    assert response.status_code == status.HTTP_200_OK
    assert 'Graphs in "default"' in response.text
    assert "graph-1" in response.text


@pytest.mark.skip
def test_graph_details_route(client: TestClient):
    """Tests the detail page for a specific graph."""
    response = client.get("/graphs/graph-1")
    assert response.status_code == status.HTTP_200_OK
    assert "Graph Details" in response.text
    assert "graph-1" in response.text


def test_settings_route(client: TestClient):
    """Tests the settings page, verifying the mock context is injected."""
    response = client.get("/settings")
    assert response.status_code == status.HTTP_200_OK
    assert "Settings" in response.text


def test_marketplace_route(client: TestClient):
    """Tests the placeholder marketplace page."""
    response = client.get("/marketplace")
    assert response.status_code == status.HTTP_200_OK
    assert "Marketplace" in response.text


def test_docs_route(client: TestClient):
    """Tests that the API documentation page loads."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "Swagger" in response.text


@pytest.mark.skip
def test_deploy_graph_get_page(client: TestClient):
    """Tests that the 'Deploy New Graph' page loads correctly."""
    response = client.get("/graphs/deploy")
    assert response.status_code == status.HTTP_200_OK
    assert "Deploy New Graph" in response.text


def test_deploy_graph_post_success(
    client: TestClient, mock_graph_service: MockGraphService
):
    """Tests the successful submission of the deploy graph form."""
    form_data = {
        "descriptor-url": "oci://my-registry/my-graph:1.0",
        "project-name": "new-project",
    }
    # Note: `url_for` generates full URLs within the test client context
    expected_redirect_url = "http://testserver/graphs/graph-from-oci"

    response = client.post("/graphs/deploy", data=form_data, follow_redirects=False)

    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == expected_redirect_url

    # Verify the mock service was called correctly
    mock_graph_service.deploy_graph.assert_called_once_with(
        "new-project", {"id": "graph-from-oci", "hdaGraph": {"id": "graph-from-oci"}}
    )

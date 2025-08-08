import pytest
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
    """Test clusters route returns successful response"""
    response = client.get("/clusters")
    assert response.status_code == status.HTTP_200_OK
    assert "Clusters" in response.text
    assert "cluster-1" in response.text
    assert "cluster-2" in response.text


def test_marketplace_route(client: TestClient):
    """Test marketplace route returns successful response"""
    response = client.get("/marketplace")
    assert response.status_code == status.HTTP_200_OK
    assert "Marketplace" in response.text


@pytest.mark.skip
def test_settings_route(client: TestClient):
    """Test settings route returns successful response"""
    response = client.get("/settings")
    assert response.status_code == status.HTTP_200_OK
    assert "Settings" in response.text

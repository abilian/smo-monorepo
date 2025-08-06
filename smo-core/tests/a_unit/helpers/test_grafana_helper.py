from unittest.mock import MagicMock, patch

import pytest
from requests.auth import HTTPBasicAuth

from smo_core.helpers.grafana.grafana_helper import GrafanaHelper


@pytest.fixture
def mock_requests():
    with patch("requests.post") as mock_post:
        yield mock_post


def test_publish_dashboard(mock_requests):
    """Test publishing a dashboard."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"url": "/d/test"}
    mock_requests.return_value = mock_response

    helper = GrafanaHelper("http://grafana", "admin", "password")
    result = helper.publish_dashboard({"dashboard": {"title": "test"}})

    assert result["url"] == "/d/test"
    mock_requests.assert_called_once_with(
        "http://grafana/api/dashboards/db",
        json={"dashboard": {"title": "test"}},
        auth=HTTPBasicAuth("admin", "password"),
    )


def test_create_cluster_dashboard():
    """Test creating a cluster dashboard."""
    helper = GrafanaHelper("http://grafana", "admin", "password")
    dashboard = helper.create_cluster_dashboard("test-cluster")
    assert dashboard["dashboard"]["title"] == "test-cluster"
    assert len(dashboard["dashboard"]["panels"]) > 0


def test_create_graph_dashboard():
    """Test creating a graph dashboard."""
    helper = GrafanaHelper("http://grafana", "admin", "password")
    dashboard = helper.create_graph_dashboard("test-graph", ["svc1", "svc2"])
    assert dashboard["dashboard"]["title"] == "test-graph"
    assert len(dashboard["dashboard"]["templating"]["list"]) == 1


def test_create_graph_service():
    """Test creating a service dashboard."""
    helper = GrafanaHelper("http://grafana", "admin", "password")
    dashboard = helper.create_graph_service("test-service")
    assert dashboard["dashboard"]["title"] == "test-service"
    assert len(dashboard["dashboard"]["panels"]) == 4

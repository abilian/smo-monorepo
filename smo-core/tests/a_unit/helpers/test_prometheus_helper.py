import math
from unittest.mock import MagicMock, patch

import pytest

from smo_core.helpers.prometheus_helper import PrometheusHelper


@pytest.fixture
def mock_requests():
    with patch("requests.get") as mock_get:
        yield mock_get


def test_get_request_rate_success(mock_requests):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"result": [{"value": [123, "15.5"]}]}}
    mock_requests.return_value = mock_response

    # Test
    helper = PrometheusHelper("http://prometheus")
    result = helper.get_request_rate_by_job("test-job")

    assert result == 15.5
    mock_requests.assert_called_once_with(
        "http://prometheus/api/v1/query",
        params={"query": 'sum(rate(http_requests_total{job="test-job"}[1m]))'},
        timeout=5,
    )


def test_get_request_rate_no_data(mock_requests):
    # Setup empty response
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"result": []}}
    mock_requests.return_value = mock_response

    # Test
    helper = PrometheusHelper("http://prometheus")
    result = helper.get_request_rate_by_job("test-job")

    assert math.isnan(result)


@patch("requests.post")
def test_update_alert_rules(mock_post, mock_requests):
    mock_post.return_value.status_code = 200
    with (
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CustomObjectsApi") as mock_coa,
    ):
        # Setup mock Kubernetes response
        mock_coa.return_value.get_namespaced_custom_object.return_value = {
            "spec": {"groups": [{"name": "smo-alerts", "rules": []}]}
        }

        # Test
        helper = PrometheusHelper("http://prometheus")
        alert = {
            "alert": "test-alert",
            "annotations": {"description": "test"},
            "expr": "test > 1",
            "for": "1m",
            "labels": {"severity": "critical"},
        }
        helper.update_alert_rules(alert, "add")

        # Verify Kubernetes API was called
        mock_coa.return_value.replace_namespaced_custom_object.assert_called_once()

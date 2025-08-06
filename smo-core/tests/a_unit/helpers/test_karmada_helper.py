from unittest.mock import MagicMock, patch

import pytest

from smo_core.helpers.karmada_helper import KarmadaHelper


@pytest.fixture
def mock_k8s_client():
    with (
        patch("kubernetes.client.CustomObjectsApi") as mock_coa,
        patch("kubernetes.client.AppsV1Api") as mock_apps,
    ):
        yield {"custom": mock_coa.return_value, "apps": mock_apps.return_value}


@patch("kubernetes.config.load_kube_config")
def test_get_cluster_info(mock_load, mock_k8s_client):
    # Setup mock response
    mock_k8s_client["custom"].list_cluster_custom_object.return_value = {
        "items": [
            {
                "metadata": {"name": "cluster1"},
                "status": {
                    "resourceSummary": {
                        "allocatable": {"cpu": "4", "memory": "16Gi"},
                        "allocated": {"cpu": "2", "memory": "8Gi"},
                    },
                    "conditions": [{"reason": "ClusterReady", "status": "True"}],
                },
            }
        ]
    }

    # Test
    helper = KarmadaHelper("/tmp/fake.config")
    result = helper.get_cluster_info()

    assert "cluster1" in result
    assert result["cluster1"]["remaining_cpu"] == 2.0
    assert result["cluster1"]["availability"] is True


@patch("kubernetes.config.load_kube_config")
def test_get_replicas(mock_load, mock_k8s_client):
    # Setup mock response
    mock_deployment = MagicMock()
    mock_deployment.status.available_replicas = 3
    mock_k8s_client["apps"].read_namespaced_deployment.return_value = mock_deployment

    # Test
    helper = KarmadaHelper("/tmp/fake.config")
    result = helper.get_replicas("test-deployment")

    assert result == 3


@patch("kubernetes.config.load_kube_config")
def test_scale_deployment(mock_load, mock_k8s_client):
    # Test
    helper = KarmadaHelper("/tmp/fake.config")
    helper.scale_deployment("test-deployment", 5)

    mock_k8s_client["apps"].patch_namespaced_deployment_scale.assert_called_once()

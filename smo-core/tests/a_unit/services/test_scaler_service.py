from unittest.mock import MagicMock

import pytest

from smo_core.services.scaler_service import ScalerService


@pytest.fixture
def mock_karmada_helper():
    helper = MagicMock()
    mock_deployment = MagicMock()
    mock_deployment.spec.replicas = 2
    mock_deployment.status.available_replicas = 2
    helper.v1_api_client.read_namespaced_deployment.return_value = mock_deployment
    return helper


@pytest.fixture
def mock_prometheus_helper():
    helper = MagicMock()
    helper.get_request_rate_by_job.return_value = 15.0
    return helper


def test_run_threshold_scaler_iteration_scale_up(
    mock_karmada_helper, mock_prometheus_helper
):
    # Setup
    mock_prometheus_helper.get_request_rate_by_job.return_value = (
        25.0  # Above threshold
    )
    scaler_service = ScalerService(mock_karmada_helper, mock_prometheus_helper)

    # Test
    result = scaler_service.run_threshold_scaler_iteration(
        "test-deployment",
        "default",
        20.0,  # scale_up_threshold
        5.0,  # scale_down_threshold
        3,  # scale_up_replicas
        1,  # scale_down_replicas
    )
    assert result["action"] == "scale_up"
    assert result["new_replicas"] == 3
    mock_karmada_helper.scale_deployment.assert_called_once_with("test-deployment", 3)


def test_run_threshold_scaler_iteration_scale_down(
    mock_karmada_helper, mock_prometheus_helper
):
    # Setup
    mock_prometheus_helper.get_request_rate_by_job.return_value = 2.0  # Below threshold
    scaler_service = ScalerService(mock_karmada_helper, mock_prometheus_helper)

    # Test
    result = scaler_service.run_threshold_scaler_iteration(
        "test-deployment",
        "default",
        20.0,  # scale_up_threshold
        5.0,  # scale_down_threshold
        3,  # scale_up_replicas
        1,  # scale_down_replicas
    )

    assert result["action"] == "scale_down"
    assert result["new_replicas"] == 1
    mock_karmada_helper.scale_deployment.assert_called_once_with("test-deployment", 1)


def test_run_threshold_scaler_iteration_no_action(
    mock_karmada_helper, mock_prometheus_helper
):
    # Setup - rate between thresholds
    mock_prometheus_helper.get_request_rate_by_job.return_value = 10.0
    scaler_service = ScalerService(mock_karmada_helper, mock_prometheus_helper)

    # Test - should not scale up or down
    result = scaler_service.run_threshold_scaler_iteration(
        "test-deployment",
        "default",
        20.0,  # scale_up_threshold
        5.0,  # scale_down_threshold
        3,  # scale_up_replicas
        1,  # scale_down_replicas
    )

    assert result["action"] == "none"
    mock_karmada_helper.scale_deployment.assert_not_called()


def test_scaler_service_run_iteration(mock_karmada_helper, mock_prometheus_helper):
    # Setup service
    service = ScalerService(
        karmada=mock_karmada_helper, prometheus=mock_prometheus_helper
    )

    # Test
    result = service.run_threshold_scaler_iteration(
        "test-deployment",
        "default",
        20.0,  # up_threshold
        5.0,  # down_threshold
        3,  # up_replicas
        1,  # down_replicas
    )

    assert "action" in result
    assert "reason" in result

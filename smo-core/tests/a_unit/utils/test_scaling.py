from unittest.mock import patch

from smo_core.utils.scaling import decide_replicas, scaling_loop


def test_decide_replicas_feasible():
    request_rates = [50, 80]
    previous_replicas = [1, 1]
    cpu_limits = [0.5, 1]
    acceleration = [False, False]
    alpha = [30, 25]
    beta = [10, 5]
    cluster_capacity = 10
    cluster_acceleration = False
    maximum_replicas = [10, 10]

    solution = decide_replicas(
        request_rates,
        previous_replicas,
        cpu_limits,
        acceleration,
        alpha,
        beta,
        cluster_capacity,
        cluster_acceleration,
        maximum_replicas,
    )

    assert solution is not None, "Expected a feasible solution"
    assert isinstance(solution, list)
    assert solution == [2, 3]
    assert len(solution) == len(request_rates)


def test_decide_replicas_infeasible_due_to_capacity():
    request_rates = [1000, 2000]
    previous_replicas = [1, 1]
    cpu_limits = [1, 1]
    acceleration = [False, False]
    alpha = [1, 1]
    beta = [0, 0]
    cluster_capacity = 10
    cluster_acceleration = False
    maximum_replicas = [100, 100]

    solution = decide_replicas(
        request_rates,
        previous_replicas,
        cpu_limits,
        acceleration,
        alpha,
        beta,
        cluster_capacity,
        cluster_acceleration,
        maximum_replicas,
    )

    assert solution is None, "Expected no solution due to infeasible capacity"


def test_decide_replicas_with_acceleration_violation():
    request_rates = [30]
    previous_replicas = [2]
    cpu_limits = [0.5]
    acceleration = [True]
    alpha = [20]
    beta = [5]
    cluster_capacity = 5
    cluster_acceleration = False
    maximum_replicas = [10]

    solution = decide_replicas(
        request_rates,
        previous_replicas,
        cpu_limits,
        acceleration,
        alpha,
        beta,
        cluster_capacity,
        cluster_acceleration,
        maximum_replicas,
    )

    assert solution is None, "Expected no solution due to acceleration policy violation"


def test_decide_replicas_minimum_replicas_constraint():
    request_rates = [0]
    previous_replicas = [2]
    cpu_limits = [1]
    acceleration = [False]
    alpha = [1]
    beta = [0]
    cluster_capacity = 10.0
    cluster_acceleration = False
    maximum_replicas = [5]

    solution = decide_replicas(
        request_rates,
        previous_replicas,
        cpu_limits,
        acceleration,
        alpha,
        beta,
        cluster_capacity,
        cluster_acceleration,
        maximum_replicas,
    )

    assert solution is not None
    assert solution == [1], "Minimum replicas should be at least 1"


def test_scaling_loop(mocker):
    """Test the scaling loop function."""
    mock_karmada = mocker.MagicMock()
    mock_karmada.get_replicas.return_value = 1
    mock_karmada.get_cpu_limit.return_value = 0.5

    mock_prom = mocker.MagicMock()
    mock_prom.get_request_rate.return_value = 10.0

    mock_stop = mocker.MagicMock()
    mock_stop.is_set.side_effect = [False, True]  # Run one iteration then stop

    # Mock KarmadaHelper to avoid loading kubeconfig
    with patch("smo_core.utils.scaling.KarmadaHelper") as mock_karmada_helper:
        mock_karmada_helper.return_value = mock_karmada

        with patch("requests.get"):
            scaling_loop(
                "test-graph",
                [False],
                [20],
                [5],
                10.0,
                False,
                [5],
                ["svc1"],
                5,
                "/tmp/kubeconfig",  # This path won't be used now
                "http://prometheus",
                mock_stop,
            )

            mock_karmada.scale_deployment.assert_called_once()

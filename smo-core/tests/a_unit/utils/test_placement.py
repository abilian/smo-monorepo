import pytest

from smo_core.utils.placement import (
    PlacementError,
    calculate_naive_placement,
    convert_placement,
    decide_placement,
    swap_placement,
)


def test_swap_placement():
    services = {"svc1": "c1", "svc2": "c2", "svc3": "c1"}
    expected = {"c1": ["svc1", "svc3"], "c2": ["svc2"]}
    assert swap_placement(services) == expected


def test_convert_placement():
    placement = [[1, 0], [0, 1]]
    services = [{"id": "svc1"}, {"id": "svc2"}]
    clusters = ["c1", "c2"]
    expected = {"svc1": "c1", "svc2": "c2"}
    assert convert_placement(placement, services, clusters) == expected


def test_decide_placement_basic():
    cluster_capacities = [4, 4]
    cluster_acceleration = [1, 1]
    cpu_limits = [2, 2]
    acceleration = [0, 1]
    replicas = [1, 2]
    current_placement = [[1, 0], [1, 0]]

    result = decide_placement(
        cluster_capacities,
        cluster_acceleration,
        cpu_limits,
        acceleration,
        replicas,
        current_placement,
    )

    assert result == [[0, 1], [1, 0]]


def test_calculate_naive_placement_valid():
    cluster_capacities = [4, 4]
    cluster_accelerations = [1, 0]
    cpu_limits = [2, 1]
    accelerations = [1, 0]
    replicas = [1, 2]

    placement = calculate_naive_placement(
        cluster_capacities, cluster_accelerations, cpu_limits, accelerations, replicas
    )

    assert placement == [[1, 0], [1, 0]]


def test_calculate_naive_placement_valid2():
    cluster_capacities = [3, 4]
    cluster_accelerations = [1, 0]
    cpu_limits = [2, 1]
    accelerations = [1, 0]
    replicas = [1, 2]  # Service 1 needs 2*1=2 CPU, Service 2 needs 1*2=2 CPU

    # Expected: service 1 (needs GPU) must go to cluster 1 (cap 3).
    # Cluster 1 has 1 CPU left.
    # Service 2 (no GPU) cannot fit in cluster 1, so must go to cluster 2 (cap 4).
    placement = calculate_naive_placement(
        cluster_capacities, cluster_accelerations, cpu_limits, accelerations, replicas
    )
    assert placement == [[1, 0], [0, 1]]


def test_calculate_naive_placement_insufficient_capacity():
    with pytest.raises(PlacementError):
        calculate_naive_placement(
            cluster_capacities=[2],
            cluster_accelerations=[1],
            cpu_limits=[3],
            accelerations=[0],
            replicas=[1],
        )


@pytest.mark.skip("Needs to be reviewed")
def test_decide_placement_basic2():
    """Test the CVXPY-based placement algorithm."""
    cluster_capacities = [4, 4]
    cluster_acceleration = [1, 1]
    cpu_limits = [2, 2]
    acceleration = [0, 1]
    replicas = [1, 2]  # Svc1: 2 cpu, Svc2: 4 cpu
    current_placement = [
        [1, 0],
        [1, 0],
    ]  # Both on cluster 1 (total 6 cpu, oversubscribes)

    # Expected: should move one service to rebalance.
    # Svc2 needs 4 cpu so it can go to either cluster
    # Svc1 needs 2 cpu and can go to either
    # Svc2 has GPU requirement, both clusters support it.
    # The most likely optimal solution is to split them to balance load
    # But objective also minimizes change. It's a complex trade-off.
    # Let's try a clearer case.

    cluster_capacities = [5, 5]
    cluster_acceleration = [1, 0]
    cpu_limits = [2, 3]
    acceleration = [1, 0]  # Svc1 needs GPU, Svc2 does not
    replicas = [1, 1]
    current_placement = [[0, 1], [1, 0]]  # Wrong placement: Svc1 on non-GPU cluster

    result = decide_placement(
        cluster_capacities,
        cluster_acceleration,
        cpu_limits,
        acceleration,
        replicas,
        current_placement,
    )

    # Expected: Svc1 MUST move to cluster 1. Svc2 can stay on cluster 1 or move to 2.
    # To minimize changes, Svc2 should stay where it can (cluster 1)
    # But Svc1 also has to go there. Total load 5. Fits.
    # So, both on cluster 1.
    assert result == [[1, 0], [1, 0]]


def test_calculate_naive_placement_single_service_too_large():
    cluster_capacities = [2]
    cluster_accelerations = [1]
    cpu_limits = [3]
    accelerations = [0]
    replicas = [1]

    with pytest.raises(PlacementError):
        calculate_naive_placement(
            cluster_capacities,
            cluster_accelerations,
            cpu_limits,
            accelerations,
            replicas,
        )


def test_calculate_naive_placement_insufficient_total_capacity():
    cluster_capacities = [2, 2]
    cluster_accelerations = [1, 1]
    cpu_limits = [2, 3]
    accelerations = [0, 1]
    replicas = [1, 1]

    with pytest.raises(PlacementError):
        calculate_naive_placement(
            cluster_capacities,
            cluster_accelerations,
            cpu_limits,
            accelerations,
            replicas,
        )

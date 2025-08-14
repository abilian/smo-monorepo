import pytest

from smo_core.services.placement_service import (
    PlacementError,
    NaivePlacementService,
    ReoptimizationPlacementService,
    convert_placement,
    swap_placement,
)


#
# Tests for Standalone Utility Functions
#
def test_swap_placement():
    """Verifies that the service->cluster dictionary is correctly inverted."""
    services = {"svc1": "c1", "svc2": "c2", "svc3": "c1"}
    expected = {"c1": ["svc1", "svc3"], "c2": ["svc2"]}
    assert swap_placement(services) == expected


def test_convert_placement():
    """Verifies that the placement matrix is correctly converted to a dictionary."""
    # Renamed variable for clarity, but the test is the same.
    placement_matrix = [[1, 0], [0, 1]]
    services = [{"id": "svc1"}, {"id": "svc2"}]
    clusters = ["c1", "c2"]
    expected = {"svc1": "c1", "svc2": "c2"}
    assert convert_placement(placement_matrix, services, clusters) == expected


#
# Tests for NaivePlacementService
#
class TestNaivePlacementService:
    """Groups all tests for the NaivePlacementService."""

    def test_calculate_naive_placement_valid(self):
        """Tests a basic valid placement scenario."""
        placer = NaivePlacementService()
        placement = placer.calculate(
            cluster_capacities=[4, 4],
            cluster_accelerations=[1, 0],
            cpu_limits=[2, 1],
            accelerations=[1, 0],
            replicas=[1, 2],
        )
        # Svc1 (2 CPU, GPU) -> cluster 1. Usage: [2, 0].
        # Svc2 (2 CPU, no GPU) -> cluster 1. Usage: [4, 0].
        assert placement == [[1, 0], [1, 0]]

    def test_calculate_naive_placement_valid_second_cluster(self):
        """Tests a scenario where the second cluster must be used."""
        placer = NaivePlacementService()
        placement = placer.calculate(
            cluster_capacities=[3, 4],
            cluster_accelerations=[1, 0],
            cpu_limits=[2, 1],
            accelerations=[1, 0],
            replicas=[1, 2],
        )
        # Svc1 (2 CPU, GPU) -> cluster 1. Usage: [2, 0].
        # Svc2 (2 CPU, no GPU) -> cannot fit in cluster 1, goes to cluster 2. Usage: [2, 2].
        assert placement == [[1, 0], [0, 1]]

    def test_calculate_naive_placement_single_service_too_large(self):
        """Verifies PlacementError is raised if a single service is too large for any cluster."""
        placer = NaivePlacementService()
        with pytest.raises(PlacementError):
            placer.calculate(
                cluster_capacities=[2],
                cluster_accelerations=[1],
                cpu_limits=[3],
                accelerations=[0],
                replicas=[1],
            )

    def test_calculate_naive_placement_insufficient_total_capacity(self):
        """Verifies PlacementError is raised if total demand exceeds total capacity."""
        placer = NaivePlacementService()
        with pytest.raises(PlacementError):
            placer.calculate(
                cluster_capacities=[2, 2],
                cluster_accelerations=[1, 1],
                cpu_limits=[2, 3],
                accelerations=[0, 1],
                replicas=[1, 1],
            )


#
# Tests for ReoptimizationPlacementService
#
class TestReoptimizationPlacementService:
    """Groups all tests for the ReoptimizationPlacementService."""

    def test_decide_placement_basic_rebalance(self):
        """Tests a basic re-balancing scenario due to over-subscription."""
        reoptimizer = ReoptimizationPlacementService()
        result = reoptimizer.calculate(
            cluster_capacities=[4, 4],
            cluster_accelerations=[1, 1],
            cpu_limits=[2, 2],
            accelerations=[0, 1],
            replicas=[1, 2], # Svc1: 2 CPU, Svc2: 4 CPU
            current_placement=[[1, 0], [1, 0]], # Both on cluster 1 (total 6 > 4)
        )
        # Expected: The model must move one service. The only valid placement is
        # Svc2 (4 CPU) on one cluster, and Svc1 (2 CPU) on the other.
        # It should solve to [[0, 1], [1, 0]] or [[1, 0], [0, 1]]. Let's accept either.
        assert result in [[[0, 1], [1, 0]], [[1, 0], [0, 1]]]

    def test_decide_placement_fix_acceleration_constraint(self):
        """Tests re-optimizing to fix a broken acceleration constraint."""
        reoptimizer = ReoptimizationPlacementService()
        result = reoptimizer.calculate(
            cluster_capacities=[5, 5],
            cluster_accelerations=[1, 0], # Only cluster 1 has GPU
            cpu_limits=[2, 3],
            accelerations=[1, 0], # Svc1 needs GPU
            replicas=[1, 1],
            current_placement=[[0, 1], [1, 0]], # Broken: Svc1 is on non-GPU cluster 2
        )
        # Expected: Svc1 MUST move to cluster 1.
        # Svc2 is on cluster 1. Total load: 2+3=5. This fits.
        # The optimal solution to minimize moves is to put both on cluster 1.
        assert result == [[1, 0], [1, 0]]

    def test_decide_placement_requires_current_placement(self):
        """Verifies that a ValueError is raised if current_placement is missing."""
        reoptimizer = ReoptimizationPlacementService()
        with pytest.raises(ValueError):
            reoptimizer.calculate(
                cluster_capacities=[5, 5],
                cluster_accelerations=[1, 0],
                cpu_limits=[2, 3],
                accelerations=[1, 0],
                replicas=[1, 1],
                current_placement=None, # Explicitly pass None
            )

    def test_decide_placement_unsolvable(self):
        """Verifies that PlacementError is raised if the problem is unsolvable."""
        reoptimizer = ReoptimizationPlacementService()
        with pytest.raises(PlacementError):
            reoptimizer.calculate(
                cluster_capacities=[1, 1], # Not enough capacity
                cluster_accelerations=[1, 1],
                cpu_limits=[2, 2],
                accelerations=[0, 0],
                replicas=[1, 1],
                current_placement=[[1, 0], [0, 1]],
            )

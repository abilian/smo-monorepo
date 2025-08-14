"""
Application node placement related functionalities.

This module defines a standard interface ('protocol') for placement services
and provides multiple implementations. It also includes utility functions for
manipulating and converting placement data structures.

Key Components:
- PlacementService (Protocol): Defines the standard API that all placement
  algorithms must implement.
- NaivePlacementService: A simple, heuristic-based implementation that places
  services on the first available cluster.
- ReoptimizationPlacementService: A more complex implementation that uses
  convex optimization to re-balance an existing placement.
"""

from typing import Protocol, List, Dict
import cvxpy as cp
import numpy as np


class PlacementError(ValueError):
    """Custom exception raised when a service placement cannot be successfully calculated."""
    pass


# ==============================================================================
# == Placement Service Protocol and Implementations
# ==============================================================================

class PlacementService(Protocol):
    """
    Defines the standard interface for a service placement algorithm.

    A class that implements this protocol must provide a `calculate` method
    that takes cluster and service data and returns a placement solution.
    """

    def calculate(
        self,
        cluster_capacities: List[float],
        cluster_accelerations: List[bool],
        cpu_limits: List[float],
        accelerations: List[bool],
        replicas: List[int],
        current_placement: List[List[int]] | None = None,
    ) -> List[List[int]]:
        """
        Calculates the placement of services onto clusters.

        Args:
            cluster_capacities: List of CPU capacity for each cluster.
            cluster_accelerations: List of GPU acceleration availability for each cluster.
            cpu_limits: List of CPU limits for each service.
            accelerations: List of GPU acceleration requirements for each service.
            replicas: List of replica counts for each service.
            current_placement: (Optional) A 2D matrix representing the current
                placement, required by re-optimization algorithms.

        Returns:
            A 2D matrix where `matrix[i][j] == 1` signifies that service `i`
            is placed on cluster `j`.

        Raises:
            PlacementError: If a valid placement cannot be found.
        """
        ...


class NaivePlacementService:
    """
    Calculates an initial placement using a first-fit heuristic.

    This service attempts to place each service sequentially onto the first
    available cluster that satisfies its resource and acceleration requirements.
    It is not globally optimal but provides a fast, deterministic initial state.
    """

    def calculate(
        self,
        cluster_capacities: List[float],
        cluster_accelerations: List[bool],
        cpu_limits: List[float],
        accelerations: List[bool],
        replicas: List[int],
        current_placement: List[List[int]] | None = None, # Not used by this strategy
    ) -> List[List[int]]:
        num_clusters = len(cluster_capacities)
        num_services = len(cpu_limits)
        service_reqs = [rep * cpu for rep, cpu in zip(replicas, cpu_limits)]

        # Pre-flight checks
        if max(service_reqs) > max(cluster_capacities):
            raise PlacementError("A single service requires more CPU than the largest cluster.")
        if sum(service_reqs) > sum(cluster_capacities):
            raise PlacementError("Insufficient total cluster capacity for all services.")

        placement = [[0] * num_clusters for _ in range(num_services)]
        cluster_usage = [0.0] * num_clusters

        for service_id, service_req in enumerate(service_reqs):
            self._place_service(
                placement, service_id, service_req, accelerations,
                cluster_capacities, cluster_accelerations, cluster_usage
            )
        return placement

    def _place_service(
        self, placement, service_id, service_req, accelerations,
        cluster_capacities, cluster_accelerations, cluster_usage
    ):
        """Private helper to place a single service using a first-fit strategy."""
        for cluster_id in range(len(cluster_capacities)):
            acceleration_ok = (not accelerations[service_id] or cluster_accelerations[cluster_id])
            capacity_ok = (cluster_usage[cluster_id] + service_req <= cluster_capacities[cluster_id])

            if acceleration_ok and capacity_ok:
                placement[service_id][cluster_id] = 1
                cluster_usage[cluster_id] += service_req
                return

        msg = f"Service {service_id} with requirement {service_req} could not be placed."
        raise PlacementError(msg)


class ReoptimizationPlacementService:
    """
    Re-optimizes an existing service placement using a convex optimization model.

    This service aims to find a new placement that minimizes both resource
    consumption and the cost of moving services from their current locations.
    """

    def calculate(
        self,
        cluster_capacities: List[float],
        cluster_accelerations: List[bool],
        cpu_limits: List[float],
        accelerations: List[bool],
        replicas: List[int],
        current_placement: List[List[int]] | None = None,
    ) -> List[List[int]]:
        if current_placement is None:
            raise ValueError("Re-optimization requires a 'current_placement' matrix.")

        num_clusters = len(cluster_capacities)
        num_services = len(cpu_limits)

        x = cp.Variable((num_services, num_clusters), boolean=True)
        y = np.array(current_placement)

        # Objective: Minimize deployment cost and the cost of moving services.
        w_dep = 1.0
        w_re = 1.0
        objective = cp.Minimize(w_dep * cp.sum(x) + w_re * cp.sum(cp.multiply(y, (y - x))))

        constraints = []
        # Constraint 1: Each service must be placed in exactly one cluster.
        for s in range(num_services):
            constraints.append(cp.sum(x[s, :]) == 1)

        # Constraint 2: Cluster capacity must not be exceeded.
        for e in range(num_clusters):
            service_demands = [cpu_limits[s] * replicas[s] for s in range(num_services)]
            constraints.append(cp.sum(cp.multiply(x[:, e], service_demands)) <= cluster_capacities[e])

        # Constraint 3: Acceleration requirements must be met.
        for s in range(num_services):
            for e in range(num_clusters):
                constraints.append(x[s, e] * accelerations[s] <= cluster_accelerations[e])

        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.HIGHS)

        if problem.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
            # In a real system, you might want to fall back to the current_placement
            # or handle this more gracefully.
            raise PlacementError(f"Optimal placement not found. Problem status: {problem.status}")

        return [
            [int(round(x.value[s, e])) for e in range(num_clusters)]
            for s in range(num_services)
        ]


# ==============================================================================
# == Standalone Utility Functions
# ==============================================================================

def swap_placement(service_dict: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Inverts a placement dictionary from service->cluster to cluster->[services].

    Args:
        service_dict: A dictionary mapping a service ID to its assigned cluster ID.

    Returns:
        A dictionary mapping a cluster ID to a list of service IDs assigned to it.
    """
    cluster_dict = {}
    for key, value in service_dict.items():
        cluster_dict.setdefault(value, []).append(key)
    return cluster_dict


def convert_placement(
    placement_matrix: List[List[int]], services: List[Dict], clusters: List[str]
) -> Dict[str, str]:
    """
    Converts a 2D placement matrix into a service-to-cluster dictionary.

    Args:
        placement_matrix: A 2D matrix where `matrix[i][j] == 1` means service `i`
            is on cluster `j`.
        services: A list of service dictionaries, each with an 'id' key.
        clusters: A list of cluster names corresponding to the matrix columns.

    Returns:
        A dictionary mapping each service ID to its assigned cluster name.
    """
    service_placement = {}
    for service_index, cluster_list in enumerate(placement_matrix):
        try:
            cluster_index = cluster_list.index(1)
            service_name = services[service_index]["id"]
            service_placement[service_name] = clusters[cluster_index]
        except ValueError:
            service_name = services[service_index]["id"]
            print(f"Warning: Service '{service_name}' was not placed on any cluster.")
    return service_placement

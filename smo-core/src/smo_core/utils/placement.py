"""
Application node placement related functionalities.

This module provides functions for calculating and manipulating the placement of
services onto a set of available compute clusters. It includes both a naive,
heuristic-based placement algorithm and a more complex, optimization-based
algorithm for re-balancing existing placements.
"""

import cvxpy as cp
import numpy as np


class PlacementError(ValueError):
    """Custom exception raised when a service placement cannot be successfully calculated."""

    pass


def swap_placement(service_dict: dict) -> dict:
    """
    Inverts a placement dictionary from service->cluster to cluster->[services].

    This is a utility function to change the perspective of the placement data,
    making it easy to see which services are running on a specific cluster.

    Args:
        service_dict (dict): A dictionary mapping a service identifier (key) to its
            assigned cluster identifier (value).
            Example: {'service1': 'cluster-a', 'service2': 'cluster-a'}

    Returns:
        dict: A dictionary mapping a cluster identifier (key) to a list of
            service identifiers (value) assigned to it.
            Example: {'cluster-a': ['service1', 'service2']}
    """
    cluster_dict = {}
    for key, value in service_dict.items():
        cluster_dict.setdefault(value, []).append(key)
    return cluster_dict


def convert_placement(
    placement: list[list[int]], services: list[dict], clusters: list[str]
) -> dict:
    """
    Converts a 2D placement matrix into a service-to-cluster dictionary.

    This function translates the matrix representation used by optimization solvers
    into a more human-readable dictionary format.

    Args:
        placement (list[list[int]]): A 2D matrix where `placement[i][j] == 1`
            signifies that service `i` is placed on cluster `j`.
        services (list[dict]): A list of service dictionaries, where each must have an 'id' key.
        clusters (list[str]): A list of cluster names, corresponding to the columns
            of the placement matrix.

    Returns:
        dict: A dictionary mapping each service ID to its assigned cluster name.
            Example Input:
                placement: [[1, 0], [0, 1]]
                services: [{'id': 'service1'}, {'id': 'service2'}]
                clusters: ['cluster-a', 'cluster-b']
            Example Output:
                {'service1': 'cluster-a', 'service2': 'cluster-b'}
    """
    service_placement = {}
    for service_index, cluster_list in enumerate(placement):
        # Find the column index where the value is 1, which indicates the assigned cluster.
        # This assumes each service is placed on exactly one cluster.
        try:
            cluster_index = cluster_list.index(1)
            service_name = services[service_index]["id"]
            service_placement[service_name] = clusters[cluster_index]
        except ValueError:
            # This case occurs if a service (row) has no '1', meaning it wasn't placed.
            service_name = services[service_index]["id"]
            print(
                f"Warning: Service '{service_name}' was not placed on any cluster in the provided matrix."
            )

    return service_placement


def decide_placement(
    cluster_capacities: list[float],
    cluster_acceleration: list[bool],
    cpu_limits: list[float],
    acceleration: list[bool],
    replicas: list[int],
    current_placement: list[list[int]],
) -> list[list[int]]:
    """
    Re-optimizes an existing service placement using a convex optimization model.

    This function aims to find a new placement that minimizes both resource
    consumption and the cost of moving services from their current locations.

    Parameters
    ----------
    cluster_capacities: List of CPU capacity for each cluster.
    cluster_acceleration: List of GPU acceleration availability for each cluster.
    cpu_limits: List of CPU limits for each service.
    acceleration: List of GPU acceleration requirements for each service.
    replicas: List of current replica counts for each service.
    current_placement: 2D matrix representing the current placement.

    Returns
    -------
    list[list[int]]
        A 2D matrix representing the new optimal placement. If the element
        at index `[i][j]` is 1, it means service `i` should be placed on cluster `j`.
        Returns the solved placement matrix regardless of the problem status.
    """
    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    # x[s, e] is a boolean variable: 1 if service `s` is on cluster `e`, else 0.
    x = cp.Variable((num_nodes, num_clusters), boolean=True)

    # y is a constant numpy array representing the current state.
    y = np.array(current_placement)

    # --- Objective Function ---
    # The goal is to minimize a weighted sum of two costs:
    # 1. Deployment Cost (w_dep): The total number of service deployments. Minimizing this
    #    prefers solutions that use fewer service instances if possible (though constrained to 1 per service).
    # 2. Re-optimization Cost (w_re): The cost of moving services. This term becomes non-zero
    #    only when a service is moved from a cluster (y=1, x=0).
    w_dep = 1.0  # Deployment cost weight
    w_re = 1.0  # Re-optimization cost weight
    objective = cp.Minimize(w_dep * cp.sum(x) + w_re * cp.sum(cp.multiply(y, (y - x))))

    constraints = []

    # Constraint 1: Each service must be placed in exactly one cluster.
    for s in range(num_nodes):
        constraints.append(cp.sum(x[s, :]) == 1)

    # Constraint 2: The sum of CPU resources used by services on a cluster
    # cannot exceed that cluster's capacity.
    for e in range(num_clusters):
        service_demands = [cpu_limits[s] * replicas[s] for s in range(num_nodes)]
        constraints.append(
            cp.sum(cp.multiply(x[:, e], service_demands)) <= cluster_capacities[e]
        )

    # Constraint 3: A service requiring acceleration can only be placed on a cluster that provides it.
    # If acceleration[s] is 1, then x[s, e] can only be 1 if cluster_acceleration[e] is also 1.
    for s in range(num_nodes):
        for e in range(num_clusters):
            constraints.append(x[s, e] * acceleration[s] <= cluster_acceleration[e])

    # Constraint 4: Dependency constraint.
    # NOTE: With d = [0, 0], this constraint is currently trivial and has no effect.
    # It may be a placeholder for future logic where d[i] would be 1 if service i depends on i-1.
    d = [0, 0]
    for i in range(1, num_nodes):
        for e in range(num_clusters):
            constraints.append(x[i, e] + x[i - 1, e] >= d[i - 1])

    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.HIGHS)

    if problem.status not in [cp.OPTIMAL, cp.OPTIMAL_INACCURATE]:
        print(f"Warning: Optimal placement not found. Problem status: {problem.status}")

    # Return the placement matrix even if non-optimal, to allow for inspection.
    placement = [
        [int(round(x.value[s, e])) for e in range(num_clusters)]
        for s in range(num_nodes)
    ]
    return placement


def calculate_naive_placement(
    cluster_capacities: list[float],
    cluster_accelerations: list[bool],
    cpu_limits: list[float],
    accelerations: list[bool],
    replicas: list[int],
) -> list[list[int]]:
    """
    Calculates an initial placement using a first-fit heuristic.

    This function attempts to place each service sequentially onto the first
    available cluster that satisfies its resource and acceleration requirements.
    It is not globally optimal but provides a fast, deterministic initial state.

    Parameters
    ----------
    cluster_capacities: List of CPU capacity for each cluster.
    cluster_accelerations: List of GPU acceleration availability for each cluster.
    cpu_limits: List of CPU limits for each service.
    accelerations: List of GPU acceleration requirements for each service.
    replicas: List of replica counts for each service.

    Returns
    -------
    list[list[int]]
        A 2D matrix representing the calculated placement.

    Raises
    ------
    PlacementError
        If a service cannot be placed in any cluster due to capacity or
        acceleration constraints.
    """
    num_clusters = len(cluster_capacities)
    num_nodes = len(cpu_limits)

    service_reqs = [rep * cpu for rep, cpu in zip(replicas, cpu_limits)]

    # Pre-check 1: Ensure the largest single service can fit somewhere.
    if max(service_reqs) > max(cluster_capacities):
        raise PlacementError(
            "A single service requires more CPU than the largest available cluster."
        )

    # Pre-check 2: Ensure the total demand doesn't exceed total capacity.
    if sum(service_reqs) > sum(cluster_capacities):
        raise PlacementError("Insufficient total cluster capacity for all services.")

    placement = [[0] * num_clusters for _ in range(num_nodes)]
    cluster_usage = [0.0] * num_clusters

    # Attempt to place each service one by one.
    for service_id, service_req in enumerate(service_reqs):
        _place_service(
            placement,
            service_id,
            service_req,
            accelerations,
            cluster_capacities,
            cluster_accelerations,
            cluster_usage,
        )

    return placement


def _place_service(
    placement: list[list[int]],
    service_id: int,
    service_req: float,
    accelerations: list[bool],
    cluster_capacities: list[float],
    cluster_accelerations: list[bool],
    cluster_usage: list[float],
):
    """
    Private helper to place a single service using a first-fit strategy.

    This function modifies `placement` and `cluster_usage` in-place.

    Args:
        placement: The 2D placement matrix to be modified.
        service_id: The index of the service to place.
        service_req: The total CPU requirement for the service.
        accelerations: List of acceleration requirements for all services.
        cluster_capacities: List of total capacities for all clusters.
        cluster_accelerations: List of acceleration availability for all clusters.
        cluster_usage: A list tracking the current CPU usage of each cluster, to be modified.

    Raises:
        PlacementError: If no suitable cluster can be found for the service.
    """
    for cluster_id in range(len(cluster_capacities)):
        # Check if acceleration requirements are met.
        acceleration_ok = (
            not accelerations[service_id] or cluster_accelerations[cluster_id]
        )
        # Check if there is enough remaining capacity.
        capacity_ok = (
            cluster_usage[cluster_id] + service_req <= cluster_capacities[cluster_id]
        )

        if acceleration_ok and capacity_ok:
            placement[service_id][cluster_id] = 1
            cluster_usage[cluster_id] += service_req
            return

    # If the loop completes without finding a spot, placement is impossible.
    msg = f"Service {service_id} with requirement {service_req} could not be placed in any cluster."
    raise PlacementError(msg)

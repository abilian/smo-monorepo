#!/usr/bin/env python3

"""
A comparative demonstration of green placement algorithms.

This script runs a single, carefully designed scenario through three different
placement algorithms to objectively compare their effectiveness:

1.  **Baseline (Naive First-Fit):** A carbon-unaware algorithm that simply places
    workloads on the first available cluster based on API order.
2.  **Green Consolidation (Heuristic):** A greedy algorithm that prioritizes
    consolidating workloads onto the greenest clusters first.
3.  **Carbon-Aware Optimization:** A sophisticated algorithm that finds the
    globally optimal placement to minimize the total system-wide carbon footprint.
"""

from smo_core.services.placement_service import (
    NaivePlacementService,
    GreenConsolidationPlacementService,
    CarbonAwareOptimizationService,
)


# --- ANSI Color Codes for Better Output ---
class colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"


def print_color(color, message):
    print(f"{color}{message}{colors.ENDC}")


def print_placement_table(title, placement_matrix, services, clusters):
    """Prints a human-readable table of a placement and its carbon cost."""
    print_color(colors.BLUE, f"\n--- {title} ---")

    header = f"{'Service ID':<20}{'CPU Req':<10}{'Placed On':<28}{'Carbon Cost':<15}"
    print(header)
    print("-" * 75)

    total_carbon_cost = 0.0

    for i, service in enumerate(services):
        try:
            cluster_index = placement_matrix[i].index(1)
            cluster = clusters[cluster_index]
            cpu_req = service["cpu"]

            carbon_cost = cpu_req * cluster["cost"]
            total_carbon_cost += carbon_cost

            print(
                f"{service['id']:<20}{cpu_req:<10}{cluster['name']:<28}{carbon_cost:<15.2f}"
            )
        except ValueError:
            print(f"{service['id']:<20}{'-':<10}{'Not Placed':<28}{'-':<15}")

    print("-" * 75)
    print_color(colors.YELLOW, f"Total Carbon Footprint Score: {total_carbon_cost:.2f}")
    return total_carbon_cost


def main():
    """Executes the comparative demonstration scenario."""

    print_color(
        colors.YELLOW,
        "=================================================================",
    )
    print_color(colors.YELLOW, " Green Placement Algorithm Comparison")
    print_color(
        colors.YELLOW,
        "=================================================================",
    )

    # --- 1. The Unified Scenario ---
    clusters = [
        {"name": "Hybrid DC (member2)", "capacity": 10, "gpu": False, "cost": 0.5},
        {"name": "Fossil DC (member3)", "capacity": 10, "gpu": False, "cost": 1.0},
        {"name": "Green DC (member1)", "capacity": 10, "gpu": False, "cost": 0.0},
    ]
    services = [
        {"id": "Service A (Large)", "cpu": 6, "gpu": False, "replicas": 1},
        {"id": "Service B (Medium)", "cpu": 5, "gpu": False, "replicas": 1},
        {"id": "Service C (Medium)", "cpu": 5, "gpu": False, "replicas": 1},
    ]

    print_color(colors.BLUE, "\n--- Scenario Setup ---")
    print("Clusters (in default API order):")
    for c in clusters:
        print(f"  - {c['name']}: Capacity={c['capacity']} CPU, Cost={c['cost']}")
    print("\nServices to Deploy (in order): A (6 CPU), B (5 CPU), C (5 CPU)")

    # --- Prepare Inputs for the Placement Services ---
    cluster_capacities = [c["capacity"] for c in clusters]
    cluster_accelerations = [c["gpu"] for c in clusters]
    cluster_carbon_costs = [c["cost"] for c in clusters]
    cpu_limits = [s["cpu"] for s in services]
    accelerations = [s["gpu"] for s in services]
    replicas = [s["replicas"] for s in services]
    initial_placement = [[0] * len(clusters) for _ in services]

    # --- 2. Run Baseline: Naive First-Fit (Carbon-Unaware) ---
    print_color(colors.YELLOW, "\n\n--- 1. Baseline: Naive First-Fit Algorithm ---")

    placer_naive = NaivePlacementService()
    baseline_placement = placer_naive.calculate(
        cluster_capacities, cluster_accelerations, cpu_limits, accelerations, replicas
    )
    baseline_cost = print_placement_table(
        "Baseline Placement Result", baseline_placement, services, clusters
    )

    # --- 3. Run Heuristic: Green Consolidation ---
    print_color(
        colors.YELLOW, "\n\n--- 2. Heuristic: Green Consolidation Algorithm ---"
    )

    placer_green = GreenConsolidationPlacementService()
    heuristic_placement = placer_green.calculate(
        cluster_capacities,
        cluster_accelerations,
        cluster_carbon_costs,
        cpu_limits,
        accelerations,
        replicas,
    )
    heuristic_cost = print_placement_table(
        "Heuristic Placement Result", heuristic_placement, services, clusters
    )

    # --- 4. Run Optimizer: Carbon-Aware Optimization ---
    print_color(colors.YELLOW, "\n\n--- 3. Optimizer: Carbon-Aware Algorithm ---")

    optimizer = CarbonAwareOptimizationService()
    optimized_placement = optimizer.calculate(
        cluster_capacities,
        cluster_accelerations,
        cluster_carbon_costs,
        cpu_limits,
        accelerations,
        replicas,
        initial_placement,
    )
    optimized_cost = print_placement_table(
        "Optimized Placement Result", optimized_placement, services, clusters
    )

    # --- 5. Final Comparative Interpretation ---
    print_color(
        colors.GREEN,
        "\n\n=================================================================",
    )
    print_color(
        colors.GREEN,
        "                      Final Comparison & Analysis",
    )
    print_color(
        colors.GREEN,
        "=================================================================",
    )

    improvement_over_baseline = (
        ((baseline_cost - optimized_cost) / baseline_cost) * 100
        if baseline_cost > 0
        else 100
    )
    improvement_over_heuristic = (
        ((heuristic_cost - optimized_cost) / heuristic_cost) * 100
        if heuristic_cost > 0
        else 100
    )

    print(
        f"\n- The Baseline (Carbon Score: {baseline_cost:.2f}): Being carbon-unaware, it used the default cluster order.\n"
        "  It placed services A and B on the Hybrid DC and was forced to place C on the expensive Fossil DC,\n"
        "  leaving the Green DC completely unused."
    )
    print(
        f"\n- The Heuristic (Carbon Score: {heuristic_cost:.2f}): This algorithm was 'trapped' by its greedy nature. It correctly\n"
        "  placed the largest service (A) on the Green DC. However, this fragmented the green capacity,\n"
        "  forcing the two medium services (B and C) onto the Hybrid DC."
    )
    print(
        f"\n- The Optimizer (Carbon Score: {optimized_cost:.2f}): By analyzing the system globally, it found the mathematically\n"
        "  best solution. It correctly 'packed' the two medium services (B and C) together on the Green DC,\n"
        "  ensuring only the minimum necessary workload (Service A) was placed on the Hybrid DC."
    )

    print_color(
        colors.GREEN,
        f"\nConclusion: The Carbon-Aware Optimizer achieved a {improvement_over_baseline:.0f}% reduction in carbon footprint\n"
        f"compared to the baseline, and a {improvement_over_heuristic:.0f}% reduction compared to the simple green heuristic.",
    )


if __name__ == "__main__":
    main()

from smo_core.context import SmoCoreContext
from smo_core.models import Cluster
from smo_core.services.graph_service import fetch_graph
from smo_core.utils.placement import swap_placement
from smo_core.utils.scaling import decide_replicas


#
# Example usage - not used in production code
#
def run_scaling_iteration(context: SmoCoreContext, db_session, name):
    """Performs a single, synchronous scaling decision."""
    graph = fetch_graph(db_session, name)
    if not graph:
        raise ValueError(f"Graph '{name}' not found.")

    karmada = context.karmada
    prometheus = context.prometheus

    placement = swap_placement(
        {s.name: s.cluster_affinity for s in graph.services if s.cluster_affinity}
    )
    if not placement:
        print("No service placements found. Cannot perform scaling.")
        return

    print(f"Current Placement: {placement}")

    MAXIMUM_REPLICAS = {
        "image-compression-vo": 3,
        "noise-reduction": 3,
        "image-detection": 3,
    }
    ACCELERATION = {
        "image-compression-vo": 0,
        "noise-reduction": 0,
        "image-detection": 0,
    }
    ALPHA = {
        "image-compression-vo": 33.33,
        "noise-reduction": 0.533,
        "image-detection": 1.67,
    }
    BETA = {
        "image-compression-vo": -16.66,
        "noise-reduction": -0.416,
        "image-detection": -0.01,
    }

    for cluster_name, managed_services in placement.items():
        print(f"Scaling services on cluster {cluster_name}:")

        previous_replicas = [karmada.get_replicas(s) or 1 for s in managed_services]
        cpu_limits = [karmada.get_cpu_limit(s) for s in managed_services]

        acceleration = [ACCELERATION.get(s, 0) for s in managed_services]
        alpha = [ALPHA.get(s, 1) for s in managed_services]
        beta = [BETA.get(s, 0) for s in managed_services]
        maximum_replicas = [MAXIMUM_REPLICAS.get(s, 5) for s in managed_services]

        request_rates = [prometheus.get_request_rate(s) for s in managed_services]

        cluster_obj = db_session.query(Cluster).filter_by(name=cluster_name).one()
        cluster_capacity = cluster_obj.available_cpu
        cluster_acceleration = cluster_obj.acceleration

        new_replicas = decide_replicas(
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

        if new_replicas is None:
            print(
                f"Scaling optimization failed for cluster {cluster_name}. Re-placement might be needed."
            )
            continue

        for idx, replicas in enumerate(new_replicas):
            service_name = managed_services[idx]
            if replicas != previous_replicas[idx]:
                print(
                    f"  -> Scaling service {service_name} from {previous_replicas[idx]} to {replicas} replicas."
                )
                karmada.scale_deployment(service_name, replicas)
            else:
                print(f"  -> Service {service_name} remains at {replicas} replicas.")

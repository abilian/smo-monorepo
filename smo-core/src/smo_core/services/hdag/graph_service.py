"""Application graph deployment business logic."""

import os
import tempfile
from pathlib import Path

import yaml
from sqlalchemy.orm.session import Session

from smo_core.models import Cluster, Graph, Service
from smo_core.utils import run_hdarctl, run_helm
from smo_core.utils.intent_translation import (
    translate_cpu,
    translate_memory,
    translate_storage,
)
from smo_core.utils.placement import (
    calculate_naive_placement,
    convert_placement,
    decide_placement,
    swap_placement,
)
from smo_core.utils.scaling import decide_replicas


def fetch_project_graphs(db_session: Session, project: str):
    """Retrieves all the descriptors of a project"""
    graphs = db_session.query(Graph).filter_by(project=project).all()
    return [graph.to_dict() for graph in graphs]


def fetch_graph(db_session: Session, name: str):
    """Retrieves the descriptor of an application graph."""
    return db_session.query(Graph).filter_by(name=name).first()


def deploy_graph(context, db_session: Session, project, graph_descriptor):
    """
    Instantiates an application graph by using Helm to
    deploy each service's artifact.
    """
    grafana_helper = context.grafana
    prom_helper = context.prometheus

    name = graph_descriptor["id"]
    if fetch_graph(db_session, name) is not None:
        raise ValueError(f"Graph with name {name} already exists")

    graph = Graph(
        name=name,
        graph_descriptor=graph_descriptor,
        project=project,
        status="Running",
        grafana=None,
    )
    db_session.add(graph)
    db_session.flush()

    services = graph_descriptor["services"]
    cpu_limits = [
        translate_cpu(s["deployment"]["intent"]["compute"]["cpu"]) for s in services
    ]
    acceleration_list = [
        1 if s["deployment"]["intent"]["compute"]["gpu"]["enabled"] == "True" else 0
        for s in services
    ]
    replicas = [1 for _ in services]

    available_clusters = db_session.query(Cluster).filter_by(availability=True).all()
    cluster_list = [c.name for c in available_clusters]
    cluster_capacity_list = [c.available_cpu for c in available_clusters]
    cluster_acceleration_list = [c.acceleration for c in available_clusters]

    service_placement = {}
    if not graph_descriptor.get("hdaGraphIntent", {}).get("useStaticPlacement", False):
        placement = calculate_naive_placement(
            cluster_capacity_list,
            cluster_acceleration_list,
            cpu_limits,
            acceleration_list,
            replicas,
        )
        graph.placement = placement
        service_placement = convert_placement(placement, services, cluster_list)
        import_clusters = create_service_imports(services, service_placement)

    svc_names = []
    for service_data in services:
        alert = {}
        svc_name = service_data["id"]
        svc_names.append(svc_name)
        artifact = service_data["artifact"]
        artifact_ref = artifact["ociImage"]
        implementer = artifact["ociConfig"]["implementer"]
        artifact_type = artifact["ociConfig"]["type"]
        values_overwrite = artifact["valuesOverwrite"]

        conditional_deployment = "event" in service_data["deployment"]["trigger"]
        if conditional_deployment:
            event = service_data["deployment"]["trigger"]["event"]["events"][0]
            alert = create_alert(
                event["id"],
                event["condition"]["promQuery"],
                event["condition"]["gracePeriod"],
                event["condition"]["description"],
                svc_name,
            )
            prom_helper.update_alert_rules(alert, "add")

        cpu = translate_cpu(service_data["deployment"]["intent"]["compute"]["cpu"])
        memory = translate_memory(
            service_data["deployment"]["intent"]["compute"]["ram"]
        )
        storage = translate_storage(
            service_data["deployment"]["intent"]["compute"]["storage"]
        )
        if service_data["deployment"]["intent"]["compute"]["gpu"]["enabled"] == "True":
            gpu = 1
        else:
            gpu = 0

        if not graph_descriptor.get("hdaGraphIntent", {}).get(
            "useStaticPlacement", False
        ):
            placement_dict = values_overwrite
            if implementer == "WOT":
                placement_dict = values_overwrite.setdefault("voChartOverwrite", {})

            placement_dict["clustersAffinity"] = [service_placement[svc_name]]
            placement_dict["serviceImportClusters"] = import_clusters[svc_name]

        status = "Pending" if conditional_deployment else "Deployed"

        svc_dashboard = grafana_helper.create_graph_service(svc_name)
        response = grafana_helper.publish_dashboard(svc_dashboard)
        grafana_url = f"{context.config['grafana']['host']}{response['url']}"

        cluster_affinity = service_placement.get(svc_name)
        service = Service(
            name=svc_name,
            values_overwrite=values_overwrite,
            graph_id=graph.id,
            status=status,
            cluster_affinity=cluster_affinity,
            artifact_ref=artifact_ref,
            artifact_type=artifact_type,
            artifact_implementer=implementer,
            cpu=cpu,
            memory=memory,
            storage=storage,
            gpu=gpu,
            grafana=grafana_url,
            alert=alert,
        )
        db_session.add(service)

        if not conditional_deployment:
            helm_install_artifact(
                context,
                svc_name,
                artifact_ref,
                values_overwrite,
                graph.project,
                "install",
            )

    dashboard = grafana_helper.create_graph_dashboard(graph.name, svc_names)
    response = grafana_helper.publish_dashboard(dashboard)
    graph.grafana = f"{context.config['grafana']['host']}{response['url']}"
    db_session.commit()


def trigger_placement(context, db_session: Session, name: str):
    graph = fetch_graph(db_session, name)
    if not graph:
        raise ValueError(f"Graph with name {name} not found")

    karmada_helper = context.karmada
    services = [s.name for s in graph.services]
    cpu_limits = [s.cpu for s in graph.services]
    acceleration_list = [s.gpu for s in graph.services]

    current_replicas = [karmada_helper.get_replicas(s) or 1 for s in services]

    available_clusters = db_session.query(Cluster).filter_by(availability=True).all()
    cluster_list = [c.name for c in available_clusters]
    cluster_capacity_list = [c.available_cpu for c in available_clusters]
    cluster_acceleration_list = [c.acceleration for c in available_clusters]

    placement = decide_placement(
        cluster_capacity_list,
        cluster_acceleration_list,
        cpu_limits,
        acceleration_list,
        current_replicas,
        graph.placement or [],
    )
    graph.placement = placement

    descriptor_services = graph.graph_descriptor["services"]
    service_placement = convert_placement(placement, descriptor_services, cluster_list)
    import_clusters = create_service_imports(descriptor_services, service_placement)

    for service in graph.services:
        values_overwrite = dict(service.values_overwrite)
        placement_dict = values_overwrite
        if service.artifact_implementer == "WOT":
            placement_dict = values_overwrite.setdefault("voChartOverwrite", {})

        if (
            placement_dict.get("clustersAffinity", [None])[0]
            != service_placement[service.name]
        ):
            placement_dict["clustersAffinity"] = [service_placement[service.name]]
            placement_dict["serviceImportClusters"] = import_clusters[service.name]
            service.values_overwrite = values_overwrite
            helm_install_artifact(
                context,
                service.name,
                service.artifact_ref,
                values_overwrite,
                graph.project,
                "upgrade",
            )

    db_session.commit()


def start_graph(context, db_session: Session, name: str) -> None:
    graph = fetch_graph(db_session, name)
    if not graph:
        raise ValueError(f"Graph {name} not found")
    if graph.status == "Running":
        raise ValueError(f"Graph {name} is already running")

    graph.status = "Running"
    for service in graph.services:
        if service.alert:
            context.prometheus.update_alert_rules(service.alert, "add")
        if service.status == "Not deployed":
            helm_install_artifact(
                context,
                service.name,
                service.artifact_ref,
                service.values_overwrite,
                graph.project,
                "install",
            )
            service.status = "Deployed"
    db_session.commit()


def stop_graph(context, db_session: Session, name: str) -> None:
    graph = fetch_graph(db_session, name)
    if not graph:
        raise ValueError(f"Graph {name} not found")
    if graph.status == "Stopped":
        raise ValueError(f"Graph {name} is already stopped")

    helm_uninstall_graph(context, graph.services, graph.project)
    graph.status = "Stopped"
    for service in graph.services:
        if service.status == "Deployed":
            service.status = "Not deployed"
    db_session.commit()


def remove_graph(context, db_session: Session, name: str) -> None:
    graph = fetch_graph(db_session, name)
    if not graph:
        raise ValueError(f"Graph {name} not found")

    if graph.status != "Stopped":
        helm_uninstall_graph(context, graph.services, graph.project)

    db_session.delete(graph)
    db_session.commit()


def deploy_conditional_service(context, db_session: Session, data: dict) -> None:
    for alert in data["alerts"]:
        labels = alert.get("labels", {})
        if "service" in labels:
            service_name = labels["service"]
            service = db_session.query(Service).filter_by(name=service_name).first()
            if not service:
                print(f"Warning: Received alert for unknown service '{service_name}'.")
                continue

            graph = service.graph
            helm_install_artifact(
                context,
                service.name,
                service.artifact_ref,
                service.values_overwrite,
                graph.project,
                "install",
            )
            service.status = "Deployed"
            db_session.commit()


def get_graph_from_artifact(artifact_ref: str) -> dict:
    """Fetches a graph descriptor from an artifact reference."""
    with tempfile.TemporaryDirectory() as dirpath:
        print(f"Pulling artifact {artifact_ref}...")
        result = run_hdarctl("pull", artifact_ref, "--untar", "--destination", dirpath)
        print(result)

        for yaml_file_path in Path(dirpath).rglob("*.yml"):
            with open(yaml_file_path, "r") as yaml_file:
                return yaml.safe_load(yaml_file)

        for yaml_file_path in Path(dirpath).rglob("*.yaml"):
            with open(yaml_file_path, "r") as yaml_file:
                return yaml.safe_load(yaml_file)

    raise FileNotFoundError("No YAML descriptor found in artifact.")


def helm_install_artifact(
    context, name, artifact_ref, values_overwrite, namespace, command
):
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yaml", delete=False
    ) as values_file:
        yaml.dump(values_overwrite, values_file)
        values_filename = values_file.name

    args = [
        command,
        name,
        artifact_ref,
        "--values",
        values_filename,
        "--namespace",
        namespace,
        "--create-namespace",
        "--kubeconfig",
        context.config["karmada_kubeconfig"],
    ]
    if context.config.get("helm", {}).get("insecure_registry"):
        args.append("--plain-http")
    if command == "upgrade":
        args.append("--reuse-values")

    print(f"Running helm {command} for service {name}...")
    result = run_helm(*args)
    print(result)
    os.remove(values_filename)


def helm_uninstall_graph(context, services, namespace):
    for service in services:
        if service.alert:
            context.prometheus.update_alert_rules(service.alert, "remove")
        if service.status == "Deployed":
            print(f"Uninstalling service {service.name}...")
            args = [
                "uninstall",
                service.name,
                "--namespace",
                namespace,
                "--kubeconfig",
                context.config["karmada_kubeconfig"],
            ]
            result = run_helm(*args)
            print(result)


def create_service_imports(services, service_placement):
    service_import_clusters = {s["id"]: [] for s in services}
    for service_data in services:
        for other_service_id in service_data["deployment"]["intent"].get(
            "connectionPoints", []
        ):
            if other_service_id in service_placement:
                service_import_clusters[other_service_id].append(
                    service_placement[service_data["id"]]
                )
    return service_import_clusters


def create_alert(event_id, prom_query, grace_period, description, name) -> dict:
    return {
        "alert": f"{event_id}",
        "annotations": {"description": description, "summary": description},
        "expr": f"{prom_query}",
        "for": f"{grace_period}",
        "labels": {"severity": "critical", "service": name},
    }


#
# Example usage - not used in production code
#
def run_scaling_iteration(context, db_session, name):
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
                print(
                    f"  -> Service {service_name} remains at {replicas} replicas."
                )

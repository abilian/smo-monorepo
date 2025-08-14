"""Application graph deployment business logic."""

import os
import tempfile
from dataclasses import dataclass

import yaml
from glom import glom
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from smo_core.helpers import KarmadaHelper, PrometheusHelper
from smo_core.helpers.grafana.grafana_helper import GrafanaHelper
from smo_core.models import Cluster, Graph, Service
from smo_core.services.placement_service import (
    NaivePlacementService,
    PlacementService,
    ReoptimizationPlacementService,
    convert_placement,
)
from smo_core.utils import run_helm
from smo_core.utils.intent_translation import (
    translate_cpu,
    translate_memory,
    translate_storage,
)


@dataclass(frozen=True)
class GraphService:
    """A service for managing the lifecycle of HDAGs."""

    db_session: Session
    karmada_helper: KarmadaHelper
    grafana_helper: GrafanaHelper
    prom_helper: PrometheusHelper
    config: dict

    # TODO: use dishka to inject these services instead
    placement_service: PlacementService = NaivePlacementService()
    reoptimization_service: PlacementService = ReoptimizationPlacementService()

    def get_graphs(self, project: str = "") -> list[Graph]:
        """Retrieves all the graph descriptors of a project"""
        stmt = select(Graph)
        if project:
            stmt = stmt.where(Graph.project == project)
        stmt = stmt.order_by(Graph.name)
        return list(self.db_session.scalars(stmt).all())

    def get_graph(self, name: str) -> Graph | None:
        """Retrieves the descriptor of an application graph."""
        return self.db_session.query(Graph).filter_by(name=name).first()

    def deploy_graph(self, project: str, graph_descriptor: dict):
        """
        Instantiates an application graph by using Helm to
        deploy each service's artifact.
        """
        # 1. Validate and create Graph DB object
        # 2. Prepare placement data (calculate_naive_placement, convert_placement)
        # 3. Prepare service imports
        # 4. Loop through services:
        #    a. Create Prometheus alert
        #    b. Translate resource intents (CPU, memory, etc.)
        #    c. Update values_overwrite with placement info
        #    d. Create service-level Grafana dashboard
        #    e. Create Service DB object
        #    f. Conditionally run helm install
        # 5. Create graph-level Grafana dashboard
        # 6. Commit transaction

        name = graph_descriptor["id"]
        if self.get_graph(name) is not None:
            raise ValueError(f"Graph with name {name} already exists")

        # 1: Create the main graph object in the database
        graph = self._create_graph_db_entry(project, graph_descriptor)

        # 2: Determine where each service should be placed
        services_descriptor = graph_descriptor["services"]
        placement_info = self._prepare_placement_info(graph, services_descriptor)

        # 3&4: Create and deploy each individual service artifact
        service_names = self._deploy_individual_services(
            graph, services_descriptor, placement_info
        )

        # 5: Create a top-level Grafana dashboard for the entire graph
        self._create_and_link_graph_dashboard(graph, service_names)

        # 6: Commit the graph and services to the database
        self.db_session.commit()

    def _create_graph_db_entry(self, project: str, graph_descriptor: dict) -> Graph:
        """Creates and saves the initial Graph entity to the database."""
        graph = Graph(
            name=graph_descriptor["id"],
            graph_descriptor=graph_descriptor,
            project=project,
            status="Running",
            grafana=None,
        )
        self.db_session.add(graph)
        self.db_session.flush()  # Use flush to get graph.id for service relationships
        return graph

    def _prepare_placement_info(self, graph: Graph, services_descriptor: list) -> dict:
        """Calculates and prepares placement and service import data."""
        if graph.graph_descriptor.get("hdaGraphIntent", {}).get(
            "useStaticPlacement", False
        ):
            return {"service_placement": {}, "import_clusters": {}}

        cluster_data = self._get_cluster_data()

        # Extract resource requirements from the service descriptors
        cpu_limits = [
            translate_cpu(s["deployment"]["intent"]["compute"]["cpu"])
            for s in services_descriptor
        ]
        acceleration_list = [
            1 if s["deployment"]["intent"]["compute"]["gpu"]["enabled"] == "True" else 0
            for s in services_descriptor
        ]

        # Calculate the placement matrix using the service
        placement_matrix = self.placement_service.calculate(
            cluster_data["capacities"],
            cluster_data["accelerations"],
            cpu_limits,
            acceleration_list,
            replicas=[1] * len(services_descriptor),
        )

        # OLD code:
        # placement_matrix = calculate_naive_placement(
        #     cluster_data["capacities"],
        #     cluster_data["accelerations"],
        #     cpu_limits,
        #     acceleration_list,
        #     replicas=[1] * len(services_descriptor),
        # )
        graph.placement = placement_matrix

        service_placement = convert_placement(
            placement_matrix, services_descriptor, cluster_data["names"]
        )
        import_clusters = self._create_service_imports(
            services_descriptor, service_placement
        )

        return {
            "service_placement": service_placement,
            "import_clusters": import_clusters,
        }

    def _deploy_individual_services(
        self, graph: Graph, services_descriptor: list, placement_info: dict
    ) -> list[str]:
        """Loops through services, creates their DB entries, and deploys them."""
        deployed_service_names = []
        for service_data in services_descriptor:
            # Build the Service database object with all its properties
            service = self._build_service_object(graph, service_data, placement_info)
            self.db_session.add(service)

            deployed_service_names.append(service.name)

            # Deploy the service now if it's not conditional
            if service.status == "Deployed":
                self._helm_install_artifact(
                    service.name,
                    service.artifact_ref,
                    service.values_overwrite,
                    graph.project,
                    "install",
                )
        return deployed_service_names

    def _build_service_object(
        self, graph: Graph, service_data: dict, placement_info: dict
    ) -> Service:
        """Builds a single Service object from its descriptor data, ready for DB insertion."""
        svc_name = service_data["id"]
        artifact = service_data["artifact"]
        values_overwrite = artifact["valuesOverwrite"]
        implementer = artifact["ociConfig"]["implementer"]

        # Handle conditional deployment alerts
        alert = {}
        is_conditional = "event" in service_data["deployment"]["trigger"]
        if is_conditional:
            event = service_data["deployment"]["trigger"]["event"]["events"][0]
            alert = self._create_alert(
                event["id"],
                event["condition"]["promQuery"],
                event["condition"]["gracePeriod"],
                event["condition"]["description"],
                svc_name,
            )
            self.prom_helper.update_alert_rules(alert, "add")

        # Update values with dynamic placement info if applicable
        if placement_info["service_placement"]:
            placement_dict = (
                values_overwrite.setdefault("voChartOverwrite", {})
                if implementer == "WOT"
                else values_overwrite
            )
            placement_dict["clustersAffinity"] = [
                placement_info["service_placement"][svc_name]
            ]
            placement_dict["serviceImportClusters"] = placement_info["import_clusters"][
                svc_name
            ]

        # Create the service's Grafana dashboard
        svc_dashboard = self.grafana_helper.create_graph_service(svc_name)
        response = self.grafana_helper.publish_dashboard(svc_dashboard)
        grafana_url = f"{self.config['grafana']['host']}{response['url']}"

        if glom(service_data, "deployment.intent.compute.gpu.enabled", default=False):
            gpu = 1
        else:
            gpu = 0

        return Service(
            name=svc_name,
            values_overwrite=values_overwrite,
            graph_id=graph.id,
            status="Pending" if is_conditional else "Deployed",
            cluster_affinity=placement_info.get("service_placement", {}).get(svc_name),
            artifact_ref=artifact["ociImage"],
            artifact_type=artifact["ociConfig"]["type"],
            artifact_implementer=implementer,
            cpu=translate_cpu(
                glom(service_data, "deployment.intent.compute.cpu", default="small")
            ),
            memory=translate_memory(
                glom(service_data, "deployment.intent.compute.ram", default="small")
            ),
            storage=translate_storage(
                glom(service_data, "deployment.intent.compute.storage", default="small")
            ),
            gpu=gpu,
            grafana=grafana_url,
            alert=alert,
        )

    def _create_and_link_graph_dashboard(self, graph: Graph, service_names: list):
        """Creates the main graph dashboard in Grafana and saves the URL."""
        dashboard = self.grafana_helper.create_graph_dashboard(
            graph.name, service_names
        )
        response = self.grafana_helper.publish_dashboard(dashboard)
        graph.grafana = f"{self.config['grafana']['host']}{response['url']}"

    def trigger_placement(self, name: str):
        graph = self.get_graph(name)
        if not graph:
            raise ValueError(f"Graph with name {name} not found")

        # 1. Gather current state data
        cluster_data = self._get_cluster_data()
        current_replicas = {
            s.name: self.karmada_helper.get_replicas(s.name) or 1
            for s in graph.services
        }

        # 2. Calculate the new placement matrix
        new_placement_matrix = self._calculate_new_placement(
            graph, cluster_data, current_replicas
        )
        graph.placement = new_placement_matrix

        # 3. Apply the changes to the services
        self._apply_placement_changes(graph, new_placement_matrix, cluster_data)

        self.db_session.commit()

    def _get_cluster_data(self) -> dict:
        """Queries the database for current cluster capacity and returns structured data."""
        available_clusters = (
            self.db_session.query(Cluster).filter_by(availability=True).all()
        )
        return {
            "names": [c.name for c in available_clusters],
            "capacities": [c.available_cpu for c in available_clusters],
            "accelerations": [c.acceleration for c in available_clusters],
        }

    def _calculate_new_placement(
        self, graph: Graph, cluster_data: dict, current_replicas: dict
    ) -> list:
        """Calculates a new placement solution for the graph."""
        services = graph.services
        service_names = [s.name for s in services]
        return self.reoptimization_service.calculate(
            cluster_capacities=cluster_data["capacities"],
            cluster_accelerations=cluster_data["accelerations"],
            cpu_limits=[s.cpu for s in services],
            accelerations=[bool(s.gpu) for s in services],
            replicas=[current_replicas[name] for name in service_names],
            current_placement=graph.placement or [],
        )
        # OLD:
        # return decide_placement(
        #     cluster_data["capacities"],
        #     cluster_data["accelerations"],
        #     [s.cpu for s in services],
        #     [s.gpu for s in services],
        #     [current_replicas[name] for name in service_names],
        #     graph.placement or [],
        # )

    def _apply_placement_changes(
        self, graph: Graph, new_placement_matrix, cluster_data
    ):
        descriptor_services = graph.graph_descriptor["services"]
        service_placement = convert_placement(
            new_placement_matrix, descriptor_services, cluster_data["names"]
        )
        import_clusters = self._create_service_imports(
            descriptor_services, service_placement
        )
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
                self._helm_install_artifact(
                    service.name,
                    service.artifact_ref,
                    values_overwrite,
                    graph.project,
                    "upgrade",
                )

    def start_graph(self, name: str) -> None:
        graph = self.get_graph(name)
        if not graph:
            raise ValueError(f"Graph {name} not found")
        if graph.status == "Running":
            raise ValueError(f"Graph {name} is already running")

        graph.status = "Running"
        for service in graph.services:
            if service.alert:
                self.prom_helper.update_alert_rules(service.alert, "add")
            if service.status == "Not deployed":
                self._helm_install_artifact(
                    service.name,
                    service.artifact_ref,
                    service.values_overwrite,
                    graph.project,
                    "install",
                )
                service.status = "Deployed"
        self.db_session.commit()

    def stop_graph(self, name: str) -> None:
        graph = self.get_graph(name)
        if not graph:
            raise ValueError(f"Graph {name} not found")
        if graph.status == "Stopped":
            raise ValueError(f"Graph {name} is already stopped")

        self._helm_uninstall_graph(graph.services, graph.project)
        graph.status = "Stopped"
        for service in graph.services:
            if service.status == "Deployed":
                service.status = "Not deployed"
        self.db_session.commit()

    def remove_graph(self, name: str) -> None:
        graph = self.get_graph(name)
        if not graph:
            raise ValueError(f"Graph {name} not found")

        if graph.status != "Stopped":
            self._helm_uninstall_graph(graph.services, graph.project)

        self.db_session.delete(graph)
        self.db_session.commit()

    def deploy_conditional_service(self, data: dict) -> None:
        for alert in data["alerts"]:
            labels = alert.get("labels", {})
            if "service" in labels:
                service_name = labels["service"]
                service = (
                    self.db_session.query(Service).filter_by(name=service_name).first()
                )
                if not service:
                    print(
                        f"Warning: Received alert for unknown service '{service_name}'."
                    )
                    continue

                graph = service.graph
                self._helm_install_artifact(
                    service.name,
                    service.artifact_ref,
                    service.values_overwrite,
                    graph.project,
                    "install",
                )
                service.status = "Deployed"
                self.db_session.commit()

    def _helm_install_artifact(
        self, name, artifact_ref, values_overwrite, namespace, command
    ):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as values_file:
            yaml.dump(values_overwrite, values_file)
            values_filename = values_file.name

        # Temp
        from pathlib import Path

        with Path("/tmp/helm_values.yaml").open("w") as f:
            yaml.dump(values_overwrite, f)

        # fmt: off
        args = [
            command,
            name,
            artifact_ref,
            "--values", values_filename,
            "--namespace", namespace,
            "--create-namespace",
            "--kubeconfig", self.config["karmada_kubeconfig"],
        ]
        # fmt: on
        if self.config.get("helm", {}).get("insecure_registry"):
            args.append("--plain-http")
        if command == "upgrade":
            args.append("--reuse-values")

        print(f"Running helm {command} for service {name}...")
        result = run_helm(*args)
        print(result)
        os.remove(values_filename)

    def _helm_uninstall_graph(self, services, namespace):
        for service in services:
            if service.alert:
                self.prom_helper.update_alert_rules(service.alert, "remove")
            if service.status == "Deployed":
                print(f"Uninstalling service {service.name}...")
                # fmt: off
                args = [
                    "uninstall",
                    service.name,
                    "--namespace", namespace,
                    "--kubeconfig", self.config["karmada_kubeconfig"],
                ]
                # fmt: on
                result = run_helm(*args)
                print(result)

    def _create_service_imports(self, services, service_placement):
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

    def _create_alert(
        self, event_id, prom_query, grace_period, description, name
    ) -> dict:
        return {
            "alert": f"{event_id}",
            "annotations": {"description": description, "summary": description},
            "expr": f"{prom_query}",
            "for": f"{grace_period}",
            "labels": {"severity": "critical", "service": name},
        }

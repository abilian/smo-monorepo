"""Kubernetes cluster business logic."""

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm.session import Session

from smo_core.helpers import KarmadaHelper
from smo_core.helpers.grafana.grafana_helper import GrafanaHelper
from smo_core.models.cluster import Cluster


@dataclass(frozen=True)
class ClusterService:
    db_session: Session
    karmada_helper: KarmadaHelper
    grafana_helper: GrafanaHelper
    config: dict

    def list_clusters(self) -> Sequence[Cluster]:
        stmt = select(Cluster).order_by(Cluster.name)
        return self.db_session.scalars(stmt).all()

    def fetch_clusters(self) -> Sequence[dict]:
        """
        Retrieves all cluster data from Karmada, syncs with the DB,
        and creates Grafana dashboards if needed.
        """
        cluster_dicts = []
        karmada_cluster_info = self.karmada_helper.get_cluster_info()

        for cluster_name, info in karmada_cluster_info.items():
            cluster = self.update_cluster(cluster_name, info)
            cluster_dicts.append(cluster.to_dict())

        self.db_session.commit()
        return cluster_dicts

    def update_cluster(self, cluster_name: str, info: dict) -> Cluster:
        stmt = select(Cluster).where(Cluster.name == cluster_name)
        cluster = self.db_session.scalars(stmt).first()
        if cluster is not None:
            cluster.available_cpu = info["remaining_cpu"]
            cluster.available_ram = info["remaining_memory_bytes"]
            cluster.availability = info["availability"]
        else:
            dashboard = self.grafana_helper.create_cluster_dashboard(cluster_name)
            response = self.grafana_helper.publish_dashboard(dashboard)
            grafana_url = f"{self.config['grafana']['host']}{response['url']}"
            cluster = Cluster(
                name=cluster_name,
                location="Unknown",
                available_cpu=info["remaining_cpu"],
                available_ram=info["remaining_memory_bytes"],
                availability=info["availability"],
                acceleration=False,  # TODO: A mechanism to discover this is needed
                grafana=grafana_url,
            )
            self.db_session.add(cluster)
        return cluster

"""Kubernetes cluster business logic."""

from smo_core.models.cluster import Cluster


def fetch_clusters(context, db_session):
    """
    Retrieves all cluster data from Karmada, syncs with the DB,
    and creates Grafana dashboards if needed.
    """
    karmada_helper = context.karmada
    grafana_helper = context.grafana

    cluster_dict = []
    karmada_cluster_info = karmada_helper.get_cluster_info()

    for cluster_name, info in karmada_cluster_info.items():
        cluster = db_session.query(Cluster).filter(Cluster.name == cluster_name).first()
        if cluster is not None:
            cluster.available_cpu = info["remaining_cpu"]
            cluster.available_ram = info["remaining_memory_bytes"]
            cluster.availability = info["availability"]
        else:
            dashboard = grafana_helper.create_cluster_dashboard(cluster_name)
            response = grafana_helper.publish_dashboard(dashboard)
            grafana_url = f"{context.config['grafana']['host']}{response['url']}"
            cluster = Cluster(
                name=cluster_name,
                location="Unknown",
                available_cpu=info["remaining_cpu"],
                available_ram=info["remaining_memory_bytes"],
                availability=info["availability"],
                acceleration=False,  # TODO: A mechanism to discover this is needed
                grafana=grafana_url,
            )
            db_session.add(cluster)

        db_session.commit()
        cluster_dict.append(cluster.to_dict())

    return cluster_dict

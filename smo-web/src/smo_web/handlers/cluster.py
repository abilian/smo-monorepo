from smo_core.services import cluster_service
from smo_web.util import get_core_context, get_db_session


def get_clusters():
    """Handler for GET /clusters, linked by operationId."""
    context = get_core_context()
    db_session = get_db_session()

    clusters = cluster_service.fetch_clusters(context, db_session)
    return clusters, 200

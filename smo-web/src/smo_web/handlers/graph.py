from smo_core.services import GraphService
from smo_web.util import get_core_context, get_db_session


def _get_graph_service() -> GraphService:
    context = get_core_context()
    db_session = get_db_session()
    graph_service = GraphService(
        db_session=db_session,
        karmada_helper=context.karmada,
        grafana_helper=context.grafana,
        prom_helper=context.prometheus,
        config=context.config,
    )
    return graph_service


def get_all_for_project(project):
    """Handler for GET /project/{project}/graphs."""
    graph_service = _get_graph_service()

    graphs = graph_service.get_graphs(project)
    return [graph for graph in graphs], 200, {"Content-Type": "application/json"}


def deploy(project, body):
    """Handler for POST /project/{project}/graphs."""
    graph_service = _get_graph_service()

    if isinstance(body, dict) and "artifact" in body:
        # FIXME
        descriptor = graph_service.get_descriptor_from_artifact(
            project, body["artifact"]
        )
    else:
        descriptor = body

    graph_descriptor = descriptor.get("hdaGraph")
    if not graph_descriptor:
        raise ValueError("hdaGraph key not found in the provided descriptor")

    graph_service.deploy_graph(project, graph_descriptor)
    return "Graph deployment triggered successfully", 202


def get_graph(name):
    graph_service = _get_graph_service()
    graph = graph_service.get_graph(name)
    if not graph:
        raise ValueError(f"Graph with name {name} not found")
    return graph.to_dict(), 200, {"Content-Type": "application/json"}


def remove(name):
    graph_service = _get_graph_service()
    graph_service.remove_graph(name)
    return (
        f"Graph {name} removed successfully",
        200,
        {"Content-Type": "application/json"},
    )


def start(name):
    graph_service = _get_graph_service()
    graph_service.start_graph(name)
    return (
        f"Graph {name} start triggered successfully",
        200,
        {"Content-Type": "application/json"},
    )


def stop(name):
    graph_service = _get_graph_service()
    graph_service.stop_graph(name)
    return (
        f"Graph {name} stop triggered successfully",
        200,
        {"Content-Type": "application/json"},
    )


def placement(name):
    graph_service = _get_graph_service()
    graph_service.start_graph(name)
    graph_service.trigger_placement(name)
    return f"Placement of graph {name} triggered", 200


def alert(body):
    graph_service = _get_graph_service()
    graph_service.deploy_conditional_service(body)
    return {"message": "Alert processed"}, 200

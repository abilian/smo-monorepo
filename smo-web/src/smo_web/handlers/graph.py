from smo_web.util import get_core_context, get_db_session

from smo_core.services.hdag import graph_service


def get_all_for_project(project):
    """Handler for GET /project/{project}/graphs."""
    db_session = get_db_session()

    graphs = graph_service.fetch_project_graphs(db_session, project)
    return [graph for graph in graphs], 200, {"Content-Type": "application/json"}


def deploy(project, body):
    """Handler for POST /project/{project}/graphs."""
    context = get_core_context()
    db_session = get_db_session()

    if isinstance(body, dict) and "artifact" in body:
        descriptor = graph_service.get_descriptor_from_artifact(
            context, project, body["artifact"]
        )
    else:
        descriptor = body

    graph_descriptor = descriptor.get("hdaGraph")
    if not graph_descriptor:
        raise ValueError("hdaGraph key not found in the provided descriptor")

    graph_service.deploy_graph(context, db_session, project, graph_descriptor)
    return "Graph deployment triggered successfully", 202


def get_graph(name):
    db_session = get_db_session()
    graph = graph_service.fetch_graph(db_session, name)
    if graph:
        return graph.to_dict(), 200, {"Content-Type": "application/json"}
    raise ValueError(f"Graph with name {name} not found")


def remove(name):
    context = get_core_context()
    db_session = get_db_session()
    graph_service.remove_graph(context, db_session, name)
    return f"Graph {name} removed successfully", 200, {"Content-Type": "application/json"}


def start(name):
    context = get_core_context()
    db_session = get_db_session()
    graph_service.start_graph(context, db_session, name)
    return f"Graph {name} start triggered successfully", 200, {"Content-Type": "application/json"}


def stop(name):
    context = get_core_context()
    db_session = get_db_session()
    graph_service.stop_graph(context, db_session, name)
    return f"Graph {name} stop triggered successfully", 200, {"Content-Type": "application/json"}


def placement(name):
    context = get_core_context()
    db_session = get_db_session()
    graph_service.trigger_placement(context, db_session, name)
    return f"Placement of graph {name} triggered", 200


def alert(body):
    context = get_core_context()
    db_session = get_db_session()
    graph_service.deploy_conditional_service(context, db_session, body)
    return {"message": "Alert processed"}, 200

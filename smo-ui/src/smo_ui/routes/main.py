from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_core.services import GraphService
from smo_core.services.cluster_service import ClusterService
from smo_ui.templating import templates

router = APIRouter(route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    cluster_service: FromDishka[ClusterService],
    graph_service: FromDishka[GraphService],
):
    clusters = cluster_service.list_clusters()
    ready_clusters = [c for c in clusters if c.availability]
    not_ready_clusters = [c for c in clusters if not c.availability]

    graphs = graph_service.get_graphs()
    active_graphs = [g for g in graphs if g.status == "Running"]
    projects = {g.project for g in graphs}

    stats = {
        "projects": len(projects),
        "graphs": len(graphs),
        "active_graphs": len(active_graphs),
        "inactive_graphs": len(graphs) - len(active_graphs),
        "clusters": len(clusters),
        "ready_clusters": len(ready_clusters),
        "not_ready_clusters": len(not_ready_clusters),
    }

    # The event log is static for now as there's no event service in smo-core
    return templates.TemplateResponse(
        request,
        "index.html",
        {"stats": stats, "active_page": "dashboard"},
    )

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from smo_core.services.cluster_service import ClusterService
from smo_core.services.graph_service import GraphService
from smo_ui.extensions import templates

router = APIRouter(route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    graph_service: FromDishka[GraphService],
    cluster_service: FromDishka[ClusterService],
):
    stats = {
        "projects": 1,
        "graphs": 1,
        "active_graphs": 1,
        "inactive_graphs": 0,
        "clusters": 1,
        "ready_clusters": 1,
        "not_ready_clusters": 0,
    }

    # The event log is static for now as there's no event service in smo-core
    return templates.TemplateResponse(
        request,
        "index.html",
        {"stats": stats, "active_page": "dashboard"},
    )


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard route that matches the template reference"""
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "stats": {
                "projects": 1,
                "graphs": 1,
                "active_graphs": 1,
                "inactive_graphs": 0,
                "clusters": 1,
                "ready_clusters": 1,
                "not_ready_clusters": 0,
            },
        },
    )

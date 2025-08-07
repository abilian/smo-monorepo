from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_core.services.graph_service import GraphService
from smo_ui.extensions import templates

router = APIRouter(prefix="/projects", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def projects(
    request: Request,
    graph_service: FromDishka[GraphService],
):
    project_stats = graph_service.get_project_stats()
    # Add some additional stats that the template might use
    total_projects = len(project_stats)
    total_graphs = sum(p.get('graph_count', 0) for p in project_stats)
    
    return templates.TemplateResponse(
        request,
        "projects.html",
        {
            "projects": project_stats,
            "total_projects": total_projects,
            "total_graphs": total_graphs,
            "active_page": "projects",
        },
    )

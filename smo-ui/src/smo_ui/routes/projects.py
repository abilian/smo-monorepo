from collections import defaultdict

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
    # Get all graphs and group by project
    graphs = graph_service.fetch_project_graphs("")  # Empty string gets all projects
    project_stats = defaultdict(lambda: {"graph_count": 0, "active_graph_count": 0})

    for graph in graphs:
        project = graph.project
        project_stats[project]["graph_count"] += 1
        if graph.status.lower() == "running":
            project_stats[project]["active_graph_count"] += 1

    # Convert to list of dicts for template
    projects_list = [{"project": p, **stats} for p, stats in project_stats.items()]
    total_projects = len(projects_list)
    total_graphs = sum(p["graph_count"] for p in projects_list)

    return templates.TemplateResponse(
        request,
        "projects.html",
        {
            "projects": projects_list,
            "total_projects": total_projects,
            "total_graphs": total_graphs,
            "active_page": "projects",
        },
    )

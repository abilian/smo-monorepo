from collections import defaultdict

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_core.services.graph_service import GraphService
from smo_ui.templating import templates

router = APIRouter(prefix="/projects", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def projects(
    request: Request,
    graph_service: FromDishka[GraphService],
):
    # Get all graphs and group by project
    graphs = graph_service.get_graphs()
    project_stats = defaultdict(lambda: {"graph_count": 0, "active_graph_count": 0})

    for graph in graphs:
        project = graph.project
        project_stats[project]["graph_count"] += 1
        if graph.status.lower() == "running":
            project_stats[project]["active_graph_count"] += 1

    # Convert to list of dicts for template
    projects_list = [{"name": p, **stats} for p, stats in project_stats.items()]
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


@router.get("/{project_name}", response_class=HTMLResponse)
async def project_details(
    request: Request,
    graph_service: FromDishka[GraphService],
):
    project_name = request.path_params["project_name"]
    graphs = graph_service.get_graphs()
    graphs = [g for g in graphs if g.project == project_name]

    graph_count = len(graphs)
    active_graph_count = sum(1 for g in graphs if g.status.lower() == "running")

    return templates.TemplateResponse(
        request,
        "project_details.html",
        {
            "project_name": project_name,
            "graphs": graphs,
            "graph_count": graph_count,
            "active_graph_count": active_graph_count,
            "active_page": "projects",
        },
    )

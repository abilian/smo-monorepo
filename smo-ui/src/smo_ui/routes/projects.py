from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from dishka.integrations.fastapi import FromDishka
from smo_core.services.graph_service import GraphService
from smo_ui.extensions import templates

router = APIRouter(prefix="/projects")


@router.get("/", response_class=HTMLResponse)
async def projects(
    request: Request,
    graph_service: FromDishka[GraphService],
):
    project_stats = graph_service.get_project_stats()

    return templates.TemplateResponse(
        request,
        "projects.html",
        {
            "projects": project_stats,
            "active_page": "projects",
        },
    )

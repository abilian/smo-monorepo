from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from dishka.integrations.fastapi import FromDishka, DishkaRoute
from smo_core.services.cluster_service import ClusterService
from smo_ui.extensions import templates

router = APIRouter(prefix="/clusters", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def clusters(
    request: Request,
    cluster_service: FromDishka[ClusterService],
):
    cluster_list = cluster_service.fetch_clusters()
    return templates.TemplateResponse(
        request,
        "clusters.html",
        {"clusters": cluster_list, "active_page": "clusters"},
    )

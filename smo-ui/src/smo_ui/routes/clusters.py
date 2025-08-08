from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from smo_core.services.cluster_service import ClusterService
from smo_ui.templating import templates

router = APIRouter(prefix="/clusters", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def clusters(
    request: Request,
    cluster_service: FromDishka[ClusterService],
):
    cluster_list = cluster_service.list_clusters()
    return templates.TemplateResponse(
        request,
        "cluster_list.html",
        {"clusters": cluster_list, "active_page": "clusters"},
    )


@router.get("/{cluster_name}", response_class=HTMLResponse)
async def cluster_details(
    request: Request,
    cluster_service: FromDishka[ClusterService],
):
    cluster_name = request.path_params["cluster_name"]
    cluster = cluster_service.get_cluster(cluster_name)
    if not cluster:
        raise HTTPException(
            status_code=404, detail=f"Cluster '{cluster_name}' not found."
        )
    return templates.TemplateResponse(
        request,
        "cluster_details.html",
        {"cluster": cluster, "active_page": "clusters"},
    )

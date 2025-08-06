from fastapi import APIRouter, Depends, Request
from fastapi1.extensions import get_db, get_smo_context, templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from smo_core.context import SmoCoreContext
from smo_core.services import cluster_service

router = APIRouter(prefix="/clusters")


@router.get("/", response_class=HTMLResponse)
async def clusters(
    request: Request,
    db: Session = Depends(get_db),
    context: SmoCoreContext = Depends(get_smo_context),
):
    cluster_list = cluster_service.fetch_clusters(context, db)
    return templates.TemplateResponse(
        request,
        "clusters.html",
        {"clusters": cluster_list, "active_page": "clusters"},
    )

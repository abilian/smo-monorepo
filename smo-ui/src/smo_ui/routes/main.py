from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from smo_core.models import Cluster, Graph
from smo_ui.extensions import get_db, templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    num_projects = db.query(func.count(Graph.project.distinct())).scalar()
    num_graphs = db.query(func.count(Graph.id)).scalar()
    num_active_graphs = (
        db.query(func.count(Graph.id)).filter(Graph.status == "Running").scalar()
    )
    num_clusters = db.query(func.count(Cluster.id)).scalar()
    num_ready_clusters = (
        db.query(func.count(Cluster.id)).filter(Cluster.availability.is_(True)).scalar()
    )

    stats = {
        "projects": num_projects,
        "graphs": num_graphs,
        "active_graphs": num_active_graphs,
        "inactive_graphs": num_graphs - num_active_graphs,
        "clusters": num_clusters,
        "ready_clusters": num_ready_clusters,
        "not_ready_clusters": num_clusters - num_ready_clusters,
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

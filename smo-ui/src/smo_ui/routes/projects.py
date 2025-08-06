from fastapi import APIRouter, Depends, Request
from fastapi1.extensions import get_db, templates
from fastapi.responses import HTMLResponse
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from smo_core.models import Graph

router = APIRouter(prefix="/projects")


@router.get("/", response_class=HTMLResponse)
async def projects(request: Request, db: Session = Depends(get_db)):
    project_stats = (
        db.query(
            Graph.project,
            func.count(Graph.id).label("graph_count"),
            func.sum(case((Graph.status == "Running", 1), else_=0)).label(
                "active_graph_count"
            ),
        )
        .group_by(Graph.project)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "projects.html",
        {
            "projects": project_stats,
            "active_page": "projects",
        },
    )

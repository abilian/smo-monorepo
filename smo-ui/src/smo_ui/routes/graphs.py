from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from dishka.integrations.fastapi import FromDishka
from smo_core.context import SmoCoreContext
from smo_core.services import graph_service
from smo_ui.extensions import templates, get_db, get_smo_context
from sqlalchemy.orm import Session

router = APIRouter(prefix="/graphs")


@router.get("/{project_name}", response_class=HTMLResponse)
async def graphs(
    request: Request,
    project_name: str,
    graph_service: FromDishka[graph_service.GraphService],
):
    graphs_list = graph_service.fetch_project_graphs(project_name)
    return templates.TemplateResponse(
        request,
        "graphs.html",
        {
            "project_name": project_name,
            "graphs": graphs_list,
            "active_page": "projects",
        },
    )


@router.get("/deploy", response_class=HTMLResponse)
async def deploy(request: Request):
    return templates.TemplateResponse(
        request, "deploy.html", {"active_page": "projects"}
    )


@router.post("/deploy", response_class=RedirectResponse)
async def deploy_post(
    request: Request,
    descriptor_url: str = Form(..., alias="descriptor-url"),
    project_name: str = Form(..., alias="project-name"),
    db: Session = Depends(get_db),
    context: SmoCoreContext = Depends(get_smo_context),
):
    try:
        graph_descriptor = graph_service.get_graph_from_artifact(descriptor_url)
        graph_service.deploy_graph(context, db, project_name, graph_descriptor)
        graph_id = graph_descriptor["id"]
        # Redirect to the new graph's detail page
        return RedirectResponse(
            url=request.url_for("graphs.graph_details", graph_id=graph_id),
            status_code=303,
        )
    except Exception as e:
        # Basic error handling: re-render form with an error message
        return templates.TemplateResponse(
            request,
            "deploy.html",
            {
                "error": f"Failed to deploy graph: {e}",
                "descriptor_url": descriptor_url,
                "project_name": project_name,
                "active_page": "projects",
            },
            status_code=400,
        )


@router.get("/{graph_id}", response_class=HTMLResponse)
async def graph_details(request: Request, graph_id: str, db: Session = Depends(get_db)):
    graph = graph_service.fetch_graph(db, graph_id)
    return templates.TemplateResponse(
        request,
        "graph_details.html",
        {
            "graph": graph.to_dict(),
            "graph_id": graph_id,
            "active_page": "projects",
        },
    )

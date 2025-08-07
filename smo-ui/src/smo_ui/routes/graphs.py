from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from smo_core.services.graph_service import GraphService
from smo_ui.templating import templates

router = APIRouter(prefix="/graphs", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def graphs_index(
    request: Request,
    graph_service: FromDishka[GraphService],
):
    # TODO: implement view
    pass


@router.get("/{project_name}", response_class=HTMLResponse)
async def graphs(
    request: Request,
    project_name: str,
    graph_service: FromDishka[GraphService],
):
    graphs_list = graph_service.get_graphs(project_name)
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
    graph_service: FromDishka[GraphService],
    descriptor_url: str = Form(..., alias="descriptor-url"),
    project_name: str = Form(..., alias="project-name"),
):
    try:
        graph_descriptor = graph_service.get_graph_from_artifact(descriptor_url)
        graph_service.deploy_graph(project_name, graph_descriptor)
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
async def graph_details(
    request: Request,
    graph_id: str,
    graph_service: FromDishka[GraphService],
):
    graph = graph_service.get_graph(graph_id)
    return templates.TemplateResponse(
        request,
        "graph_details.html",
        {
            "graph": graph.to_dict(),
            "graph_id": graph_id,
            "active_page": "projects",
        },
    )

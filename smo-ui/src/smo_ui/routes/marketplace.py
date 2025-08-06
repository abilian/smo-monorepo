from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from dishka.integrations.fastapi import DishkaRoute

from smo_ui.extensions import templates

router = APIRouter(prefix="/marketplace", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse(request, "marketplace.html")

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_ui.templating import templates

router = APIRouter(prefix="/marketplace", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse(request, "marketplace.html")

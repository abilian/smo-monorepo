from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_ui.config import Config
from smo_ui.templating import templates

router = APIRouter(prefix="/settings", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def settings(request: Request, config: FromDishka[Config]):
    return templates.TemplateResponse(
        request,
        "settings.html",
        {"config": config, "active_page": "settings"},
    )

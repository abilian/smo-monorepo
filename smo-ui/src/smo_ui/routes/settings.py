from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_core.context import SmoCoreContext
from smo_ui.templating import templates

router = APIRouter(prefix="/settings", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def settings(
    request: Request,
    context: FromDishka[SmoCoreContext],
):
    return templates.TemplateResponse(
        request,
        "settings.html",
        {"config": context.config, "active_page": "settings"},
    )

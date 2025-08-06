from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_ui.extensions import templates

router = APIRouter(prefix="/events", route_class=DishkaRoute)


@router.get("/", response_class=HTMLResponse)
async def events(request: Request):
    return templates.TemplateResponse(request, "events.html")

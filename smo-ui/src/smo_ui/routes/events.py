from fastapi import APIRouter, Request
from fastapi1.extensions import templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/events")


@router.get("/", response_class=HTMLResponse)
async def events(request: Request):
    return templates.TemplateResponse(request, "events.html")

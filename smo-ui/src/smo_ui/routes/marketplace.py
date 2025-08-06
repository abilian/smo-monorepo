from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_ui.extensions import templates

router = APIRouter(prefix="/marketplace")


@router.get("/", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse(request, "marketplace.html")

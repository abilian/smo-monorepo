from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from smo_ui.extensions import templates

router = APIRouter(prefix="/docs")


@router.get("/", response_class=HTMLResponse)
async def docs(request: Request):
    return templates.TemplateResponse(request, "docs.html")

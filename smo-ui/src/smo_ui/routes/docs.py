from fastapi import APIRouter, Request
from fastapi1.extensions import templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/docs")


@router.get("/", response_class=HTMLResponse)
async def docs(request: Request):
    return templates.TemplateResponse(request, "docs.html")

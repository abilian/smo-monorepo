from fastapi import APIRouter, Request
from fastapi1.extensions import templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/marketplace")


@router.get("/", response_class=HTMLResponse)
async def marketplace(request: Request):
    return templates.TemplateResponse(request, "marketplace.html")

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from smo_core.context import SmoCoreContext
from smo_ui.extensions import get_smo_context, templates

router = APIRouter(prefix="/settings")


@router.get("/", response_class=HTMLResponse)
async def settings(
    request: Request, context: SmoCoreContext = Depends(get_smo_context)
):
    return templates.TemplateResponse(
        request,
        "settings.html",
        {"config": context.config, "active_page": "settings"},
    )

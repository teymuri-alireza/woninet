from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from woninet.server.dependencies import get_static_path

TEMPLATES_DIR, STATIC_DIR = get_static_path()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/about", tags=["about"])


@router.get("", response_class=HTMLResponse)
def about(request: Request):
    from woninet.__init__ import __version__

    return templates.TemplateResponse(
        request=request,
        name="about.html",
        context={
            "version": __version__,
            "github_url": "https://github.com/teymuri-alireza/woninet",
        },
    )

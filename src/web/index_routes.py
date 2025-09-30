from fastapi import APIRouter, Request
from starlette.templating import _TemplateResponse
from fastapi.templating import Jinja2Templates

from config import Config

router = APIRouter()

template_obj = Jinja2Templates(directory=Config.templates_dir)


@router.get("/", name="main", response_class=_TemplateResponse)
def index(request: Request) -> _TemplateResponse:
    return template_obj.TemplateResponse({"request": request}, "index.html")

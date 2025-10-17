from fastapi import APIRouter, Request, status
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from web.base_routes import BaseRouter

router = APIRouter()


@cbv(router)
class Main(BaseRouter):
    @router.get(
        "/",
        status_code=status.HTTP_200_OK,
        name="main",
        response_class=_TemplateResponse
    )
    def index(self, request: Request) -> _TemplateResponse:
        return self.template.TemplateResponse({"request": request}, "index.html")

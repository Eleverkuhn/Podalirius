from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

from web.base_routes import BaseRouter

router = APIRouter(prefix="/services")


@cbv(router)
class Service(BaseRouter):
    @router.get("/{title}", name="service", status_code=status.HTTP_200_OK)
    def get(self, title: str) -> None:
        pass

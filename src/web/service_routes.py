from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/services")


@cbv(router)
class Service:
    @router.get("/", status_code=status.HTTP_200_OK)  # TODO: Remove. This endpoint doesn't exist
    def get_all(self) -> None:
        pass

    @router.get("/{title}", status_code=status.HTTP_200_OK)
    def get(self, title: str) -> None:
        pass

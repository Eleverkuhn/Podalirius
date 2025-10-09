from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/specialties")


@cbv(router)
class Specialty:
    @router.get("/", name="all", status_code=status.HTTP_200_OK)
    def get_all(self) -> None:
        pass

    @router.get("/{title}", name="specialty", status_code=status.HTTP_200_OK)
    def get(self, title: str) -> None:
        pass

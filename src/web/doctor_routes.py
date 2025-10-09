from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/doctors")


@cbv(router)
class Doctor:
    @router.get("/{id}", name="doctor", status_code=status.HTTP_200_OK)
    def get(self, id: str) -> None:
        pass

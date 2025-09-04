from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

router = APIRouter(prefix="/appointments")


@cbv(router)
class Appointment:
    @router.get("/", status_code=status.HTTP_200_OK)
    def get_appointment(self) -> None:
        pass

    @router.post("/", status_code=status.HTTP_201_CREATED)
    def create_appointment(self) -> None:
        pass

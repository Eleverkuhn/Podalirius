from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

from logger.setup import get_logger
from service.form_services import get_reschedule_data_constructor
from web.base_routes import BaseRouter

router = APIRouter(prefix="/doctors")


@cbv(router)
class Doctor(BaseRouter):
    @router.get("/{id}", name="doctor", status_code=status.HTTP_200_OK)
    def get(self, id: str) -> None:
        pass

    @router.get(
        "/{id}/schedule",
        name="schedule",
        response_class=JSONResponse,
        status_code=status.HTTP_200_OK
    )
    def schedule(
            self,
            id: str,
            constructor=Depends(get_reschedule_data_constructor)
    ):
        appointment_schedule = constructor.exec()
        return appointment_schedule
        # response = {"schedule": appointment_schedule}
        # return response

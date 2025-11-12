from fastapi import APIRouter, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from service.doctor_services import DoctorPage, get_doctor_page
from service.form_services import get_reschedule_data_constructor
from web.base_routes import BaseRouter

router = APIRouter(prefix="/doctors")


@cbv(router)
class Doctor(BaseRouter):
    @router.get("/{id}", name="doctor", status_code=status.HTTP_200_OK)
    def get(
            self,
            request: Request,
            id: str,
            doctor_page: DoctorPage = Depends(get_doctor_page)
    ) -> _TemplateResponse:
        doctor = doctor_page.get_detailed_info(int(id))
        content = {"request": request, "doctor": doctor}
        response = self.template.TemplateResponse(
            "doctor_detail.html", content
        )
        return response

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

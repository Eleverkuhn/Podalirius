from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from logger.setup import get_logger
from model.form_models import RescheduleAppointmentForm
from web.base_routes import Prefixes, BaseRouter
from service.patient_services import PatientPage, get_patient_page
from data.sql_models import Status

patient_appointments_router = APIRouter(prefix=f"{Prefixes.MY}/appointments")
patient_info_router = APIRouter(prefix=f"{Prefixes.MY}/info")


@cbv(patient_appointments_router)
class PatientAppointment(BaseRouter):
    @patient_appointments_router.get(
        "/",
        name="all",
        status_code=status.HTTP_200_OK,
    )
    def get_all(
            self,
            request: Request,
            appointment_status: str = "pending",
            patient_page: PatientPage = Depends(get_patient_page)
    ) -> _TemplateResponse:
        appointments = patient_page.get_appointments(appointment_status)
        content = {"request": request, "appointments": appointments}
        response = self.template.TemplateResponse(
            "my_appointments.html", content
        )
        return response

    @patient_appointments_router.get(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def get(
            self,
            request: Request,
            id: str,
            patient_page: PatientPage = Depends(get_patient_page)
    ) -> _TemplateResponse:
        appointment = patient_page.get_appointment(int(id))
        content = {"request": request, "appointment": appointment}
        response = self.template.TemplateResponse(
            "my_appointment_info.html", content
        )
        return response

    @patient_appointments_router.put(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK
    )
    def update(
            self,
            request: Request,
            id: str,
            form: RescheduleAppointmentForm,
            patient_page: PatientPage = Depends(get_patient_page)
    ) -> RedirectResponse:
        appointment_id = self._convert_appointment_id(id)
        patient_page.reschedule_appointment(appointment_id, form)
        url = request.app.url_path_for("PatientAppointment.appointment", id=id)
        response = RedirectResponse(
            url=url, status_code=status.HTTP_303_SEE_OTHER
        )
        return response

    @patient_appointments_router.patch(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK
    )
    def cancel(
            self,
            request: Request,
            id: str,
            patient_page: PatientPage = Depends(get_patient_page)
    ) -> RedirectResponse:
        appointment_id = self._convert_appointment_id(id)
        patient_page.change_appointment_status(appointment_id, Status.CANCELLED)
        url = request.app.url_path_for("PatientAppointment.appointment", id=id)
        response = RedirectResponse(
            url=url, status_code=status.HTTP_303_SEE_OTHER
        )
        return response

    def _convert_appointment_id(self, id: str) -> int:
        id = int(id)
        return id


@cbv(patient_info_router)
class PatientInfo(BaseRouter):
    @patient_info_router.get(
        "/", name="info", status_code=status.HTTP_200_OK)
    def get(
            self,
            request: Request,
            patient_page: PatientPage = Depends(get_patient_page)
    ) -> _TemplateResponse:
        content = {"request": request, "patient": patient_page.patient_public}
        response = self.template.TemplateResponse("my_info.html", content)
        return response


    @patient_info_router.put(
        "/", name="info", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

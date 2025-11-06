from fastapi import APIRouter, Depends, status, Request
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse

from logger.setup import get_logger
from web.base_routes import Prefixes, BaseRouter
from service.patient_services import PatientPage, get_patient_page

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
        return self.template.TemplateResponse("my_appointments.html", content)

    @patient_appointments_router.get(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def get(self) -> None:
        pass

    @patient_appointments_router.put(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

    @patient_appointments_router.patch(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def cancel(self) -> None:
        pass


@cbv(patient_info_router)
class PatientInfo(BaseRouter):
    @patient_info_router.get(
        "/", name="info", status_code=status.HTTP_200_OK)
    def get(self) -> None:
        pass

    @patient_info_router.put(
        "/", name="info", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv

from service.appointment_services import AppointmentBooking

router = APIRouter(prefix="/appointments")


@cbv(router)
class Appointment:
    @router.get(
        "/", name="get_appointment_form", status_code=status.HTTP_200_OK)
    def get_appointment(self) -> None:
        pass

    @router.post("/new", name="create_appointment", status_code=status.HTTP_201_CREATED)
    def create_appointment(
            self,
            appointment: AppointmentBooking = Depends()) -> RedirectResponse:
        response = appointment.response
        return response

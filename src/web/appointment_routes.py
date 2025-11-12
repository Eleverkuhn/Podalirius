from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from jose.exceptions import ExpiredSignatureError
from starlette.templating import _TemplateResponse

from web.base_routes import BaseRouter
from model.form_models import AppointmentBookingForm
from service.appointment_services import (
    AppointmentBooking,
    get_appointment_booking,
    AppointmentJWTTokenService,
    get_appointment_jwt_token_service
)
from service.form_services import get_booking_form_data_constructor

router = APIRouter(prefix="/appointments")


@cbv(router)
class Appointment(BaseRouter):
    @router.get(
        "/new",
        name="get_form",
        status_code=status.HTTP_200_OK,
        response_class=_TemplateResponse
    )
    def get_appointment(
            self,
            request: Request,
            form_content=Depends(get_booking_form_data_constructor)
    ) -> _TemplateResponse:
        form = form_content.exec()
        content = {"request": request, "form": form}
        return self.template.TemplateResponse("appointment_new.html", content)

    @router.post(
        "/new",
        name="send_form",
        status_code=status.HTTP_303_SEE_OTHER,
        response_class=RedirectResponse
    )
    def create_appointment(
            self,
            form: AppointmentBookingForm = Depends(AppointmentBookingForm.as_form),
            service: AppointmentBooking = Depends(get_appointment_booking)
    ) -> RedirectResponse:
        response = service.exec(form)
        return response

    @router.get("/view", name="info", status_code=status.HTTP_200_OK)
    def created_info(
            self,
            request: Request,
            token: str,
            service: AppointmentJWTTokenService = Depends(
                get_appointment_jwt_token_service
            )
    ) -> None:
        try:
            appointment = service.get_appointment(token)
        except ExpiredSignatureError:
            response = RedirectResponse(
                url=request.app.url_path_for("Main.main"),
                status_code=status.HTTP_303_SEE_OTHER
            )
            return response
        else:
            content = {"request": request, "appointment": appointment}
            response = self.template.TemplateResponse(
                "appointment_notification.html", content
            )
            return response

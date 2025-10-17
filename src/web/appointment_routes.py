from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from jose.exceptions import ExpiredSignatureError
from starlette.templating import _TemplateResponse

from web.base_routes import BaseRouter
from service.appointment_services import (
    AppointmentBooking,
    AppointmentJWTTokenService,
    get_appointment_booking,
    post_appointment_booking,
    get_appointment_jwt_token_service
)

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
            service: AppointmentBooking = Depends(get_appointment_booking)
    ) -> _TemplateResponse:
        user = service.render_form()
        content = {
            "request": request,
            "form": service.form.model_dump(),
            "user": user
        }
        return self.template.TemplateResponse("appointment_new.html", content)

    @router.post(
        "/new",
        name="send_form",
        status_code=status.HTTP_303_SEE_OTHER,
        response_class=RedirectResponse
    )
    def create_appointment(
            self,
            request: Request,
            service: AppointmentBooking = Depends(post_appointment_booking)):
        token = service.book()
        url = request.app.url_path_for("Appointment.info")
        modified = "".join([url, f"?token={token}"])
        response = RedirectResponse(
            url=modified,
            status_code=status.HTTP_303_SEE_OTHER
        )
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

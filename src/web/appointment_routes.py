from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_utils.cbv import cbv
from jose.exceptions import ExpiredSignatureError
from starlette.templating import _TemplateResponse
from pydantic import ValidationError

from config import Config
from exceptions import DataDoesNotMatch
from service.appointment_services import (
    AppointmentBooking,
    AppointmentJWTTokenService,
    get_appointment_booking,
    post_appointment_booking,
    get_appointment_jwt_token_service
)

router = APIRouter(prefix="/appointments")
template_obj = Jinja2Templates(directory=Config.templates_dir)


@cbv(router)
class Appointment:
    @router.get(
        "/new",
        name="get_appointment_form",
        status_code=status.HTTP_200_OK,
        response_class=_TemplateResponse)
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
        return template_obj.TemplateResponse("appointment_new.html", content)

    @router.post(
        "/new",
        name="create_appointment",
        status_code=status.HTTP_303_SEE_OTHER,
        response_class=RedirectResponse
    )
    def create_appointment(
            self,
            request: Request,
            service: AppointmentBooking = Depends(post_appointment_booking)):
        try:
            token = service.book()
        except ValidationError as exc:
            content = {
                "request": request,
                "form": service.form.model_dump(),
                "errors": exc.errors()
            }
            return template_obj.TemplateResponse(
                "appointment_new.html", content
            )
        except DataDoesNotMatch as exc:
            content = {
                "request": request,
                "unmatching_exc": exc,
                "form": service.form.model_dump()
            }
            return template_obj.TemplateResponse(
                "appointment_new.html", content
            )
        else:
            url = request.app.url_path_for("Appointment.appointment_created")
            modified = "".join([url, f"?token={token}"])
            response = RedirectResponse(
                url=modified,
                status_code=status.HTTP_303_SEE_OTHER
            )
            return response

    @router.get(
        "/view",
        name="appointment_created",
        status_code=status.HTTP_200_OK,
    )
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
                url=request.app.url_path_for("main"),
                status_code=status.HTTP_303_SEE_OTHER
            )
            return response
        else:
            content = {"request": request, "appointment": appointment}
            response = template_obj.TemplateResponse(
                "appointment_notification.html", content
            )
            return response

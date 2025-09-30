from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_utils.cbv import cbv
from starlette.templating import _TemplateResponse
from pydantic import ValidationError

from config import Config
from service.appointment_services import (
    AppointmentBooking,
    get_appointment_booking,
    post_appointment_booking
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
            response_class=RedirectResponse)
    def create_appointment(
            self,
            request: Request,
            service: AppointmentBooking = Depends(post_appointment_booking)):
        try:
            service.render_form()
        except ValidationError as exc:
            content = {
                "request": request,
                "form": service.form.model_dump(),
                "errors": exc.errors()
            }
            return template_obj.TemplateResponse("appointment_new.html", content)
        else:
            response = RedirectResponse(
                url=request.app.url_path_for("main"),
                status_code=status.HTTP_303_SEE_OTHER)
            return response

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates

from logger.setup import get_logger
from config import Config

template_obj = Jinja2Templates(directory=Config.templates_dir)


class DataDoesNotMatch(ValueError):  # REF: move it in distinct file
    default_message = (
        "The data provided with the phone number does not match. "
        "Please log in to book an appointment or provide a different phone."
    )

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


async def render_data_does_not_match(
    request: Request, exc: DataDoesNotMatch
):
    form = await request.form()
    content = {
        "request": request,
        "unmatching_exc": exc,
        "form": form
    }
    return template_obj.TemplateResponse(
        "appointment_new.html",
        content,
        status_code=status.HTTP_400_BAD_REQUEST
    )


async def render_template_with_error_message(  # REF: rename
        request: Request, exc: RequestValidationError):
    form = await request.form()
    errors = {
        error.get("loc")[0]: error.get("msg")
        for error in
        exc.errors()
    }
    content = {
        "request": request,
        "errors": errors,
        "form": form,
    }
    if request.url.path == request.url_for("Login.form").path:
        template = "login.html"
    elif request.url.path == request.url_for("Appointment.send_form").path:
        template = "appointment_new.html"
    return template_obj.TemplateResponse(
        # "appointment_new.html",
        template,
        content,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

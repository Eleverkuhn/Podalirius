from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse

from exceptions.exc import FormInputError
from logger.setup import get_logger
from config import Config

template_obj = Jinja2Templates(directory=Config.templates_dir)


async def form_input_err_handler(
        request: Request, exc: FormInputError
) -> _TemplateResponse:
    form = await request.form()
    content = {
        "request": request,
        "form_input_err": str(exc),
        "form": form
    }
    if request.url.path == request.url_for("Appointment.send_form").path:
        template = "appointment_new.html"
    elif request.url.path == request.url_for("VerifyCode.form").path:
        template = "verify_login.html"
    return template_obj.TemplateResponse(
        template,
        content,
        status_code=status.HTTP_400_BAD_REQUEST
    )


async def req_validation_err_handler(
        request: Request, exc: RequestValidationError
) -> _TemplateResponse:
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
    elif request.url.path == request.url_for("VerifyCode.form").path:
        template = "verify_login.html"
    return template_obj.TemplateResponse(
        template,
        content,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

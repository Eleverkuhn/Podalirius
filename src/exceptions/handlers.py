from typing import override

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.templating import Jinja2Templates

from exceptions.exc import (
    FormInputError, UnauthorizedError, AccessTokenExpired
)
from logger.setup import get_logger
from config import Config
from web.base_routes import BaseRouter

template_obj = Jinja2Templates(directory=Config.templates_dir)


class BaseExcHandler(BaseRouter):
    def __init__(self, request: Request = None, form=None) -> None:
        self.request = request
        self.form = form

    async def __call__(self, request: Request):
        self.request = request
        self.form = await request.form()

    @property
    def url_path_to_template(self) -> dict[str, str]:
        return {
            self.request.url_for("Login.form").path: "login.html",
            self.request.url_for("VerifyCode.form").path: "verify_login.html",
            self.request.url_for("Appointment.send_form").path: "appointment_new.html",
            self.request.url_for("PatientInfo.info").path: "my_info.html"
        }


class UnauthorizedErrorHandler:
    async def __call__(self, request: Request, exc: UnauthorizedError):
        return RedirectResponse(
            url=request.url_for("Main.main").path,
            status_code=status.HTTP_303_SEE_OTHER
        )


class FormInputErrHandler(BaseExcHandler):
    @override
    async def __call__(self, request: Request, exc: FormInputError):
        await super().__call__(request)
        return self.template.TemplateResponse(
            self.url_path_to_template.get(self.request.url.path),
            {
                "request": self.request,
                "form_input_err": str(exc),
                "form": self.form
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )


class RequestValidationErrorHandler(BaseExcHandler):
    async def __call__(self, request: Request, exc: RequestValidationError):
        await super().__call__(request)
        errors = {
            error.get("loc")[0]: error.get("msg")
            for error in
            exc.errors()
        }
        get_logger().debug(errors)
        print(f"ERRORS: {errors}")
        return self.template.TemplateResponse(
            self.url_path_to_template.get(self.request.url.path),
            {
                "request": self.request,
                "errors": errors,
                "form": self.form
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AccessTokenExpiredHandler:
    async def __call__(self, request: Request, exc: AccessTokenExpired):
        response = RedirectResponse(
            url=self._construct_url(request),
            status_code=status.HTTP_303_SEE_OTHER
        )
        return response

    def _construct_url(self, request: Request) -> str:
        original_url = request.url.path
        refresh_url = request.url_for("Refresh.refresh").path
        combined_url = f"{refresh_url}?next={original_url}"
        get_logger().debug(combined_url)
        return combined_url

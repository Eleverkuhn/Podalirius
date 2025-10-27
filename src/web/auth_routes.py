from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from pydantic import ValidationError
from starlette.templating import _TemplateResponse
from sqlmodel import Session

from logger.setup import get_logger
from web.base_routes import BaseRouter, Prefixes
from model.form_models import PhoneForm, OTPCodeForm
from service.auth_services import AuthService, OTPCodeService
from data.connections import MySQLConnection

login_router = APIRouter(prefix=f"{Prefixes.AUTH}/login")
verify_code_router = APIRouter(prefix=f"{Prefixes.AUTH}/verify-code")


@cbv(login_router)
class Login(BaseRouter):
    @login_router.get(
        "/",
        name="form",
        status_code=status.HTTP_200_OK,
    )
    def get_form(self, request: Request) -> _TemplateResponse:
        content = {"request": request}
        return self.template.TemplateResponse("login.html", content)

    @login_router.post(
        "/", status_code=status.HTTP_303_SEE_OTHER, name="form")
    def send_form(
            self,
            request: Request,
            form: PhoneForm = Depends(PhoneForm.as_form),
    ) -> RedirectResponse:
        try:
            OTPCodeService().create(form.phone)
        except ValidationError as exc:
            content = {
                "request": request,
                "form": form.model_dump(),
                "errors": exc.errors()
            }
            return self.template.TemplateResponse("login.html", content)
        else:
            response = RedirectResponse(
                url=request.app.url_path_for("VerifyCode.form"),
                status_code=status.HTTP_303_SEE_OTHER
            )
            return response


@cbv(verify_code_router)
class VerifyCode(BaseRouter):
    @verify_code_router.get(
        "/", status_code=status.HTTP_200_OK, name="form"
    )
    def get_form(self, request: Request) -> _TemplateResponse:
        content = {"request": request}
        return self.template.TemplateResponse("verify_login.html", content)

    @verify_code_router.post(
        "/", status_code=status.HTTP_303_SEE_OTHER, name="form"
    )
    def send_form(
            self,
            request: Request,
            session: Session = Depends(MySQLConnection.get_session),
            form: OTPCodeForm = Depends(OTPCodeForm.as_form)
    ) -> RedirectResponse:
        response = RedirectResponse(
            url=request.app.url_path_for("PatientAppointment.all"),
            status_code=status.HTTP_303_SEE_OTHER
        )
        AuthService(session).authenticate(form, response)
        get_logger().debug(response.headers)
        return response

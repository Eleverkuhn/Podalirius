from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from pydantic import ValidationError
from starlette.templating import _TemplateResponse
from sqlmodel import Session

from logger.setup import get_logger
from web.base_routes import BaseRouter, Prefixes
from model.form_models import PhoneForm, OTPCodeForm
from service.auth_services import AuthService, OTPCodeService, get_auth_service
from data.connections import MySQLConnection

login_router = APIRouter(prefix=f"{Prefixes.AUTH}/login")
verify_code_router = APIRouter(prefix=f"{Prefixes.AUTH}/verify-code")
refresh_router = APIRouter(prefix=f"{Prefixes.AUTH}/refresh")


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
    @verify_code_router.get("/", status_code=status.HTTP_200_OK, name="form")
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
        AuthService(session, request).authenticate(form, response)
        return response


@cbv(refresh_router)
class Refresh(BaseRouter):
    @refresh_router.get("/", status_code=status.HTTP_200_OK, name="refresh")
    def refresh(
            self,
            request: Request,
            auth: AuthService = Depends(get_auth_service)
    ) -> RedirectResponse:
        next_url = request.query_params.get("next")
        get_logger().debug(request.cookies)
        response = RedirectResponse(
            url=next_url, status_code=status.HTTP_303_SEE_OTHER
        )
        auth.refresh_access_token(response)
        return response

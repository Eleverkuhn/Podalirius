from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv
from pydantic import ValidationError
from starlette.templating import _TemplateResponse
from sqlmodel import Session

from config import Config
from web.routes import Prefixes
from model.form_models import PhoneForm, OTPCodeForm
from service.auth_services import AuthService, OTPCodeService
from data.mysql import get_session

login_router = APIRouter(prefix=f"{Prefixes.AUTH}/login")
verify_code_router = APIRouter(prefix=f"{Prefixes.AUTH}/verify-code")
template_obj = Jinja2Templates(directory=Config.templates_dir)


@cbv(login_router)
class Login:
    @login_router.get(
        "/",
        name="form",
        status_code=status.HTTP_200_OK,
    )
    def get_form(
            self, request: Request, form: PhoneForm = Depends(PhoneForm.empty)
    ) -> _TemplateResponse:
        content = {"request": request, "form": form.model_dump()}
        return template_obj.TemplateResponse("login.html", content)

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
            return template_obj.TemplateResponse("login.html", content)
        else:
            response = RedirectResponse(
                url=request.app.url_path_for("VerifyCode.form"),
                status_code=status.HTTP_303_SEE_OTHER
            )
            return response


@cbv(verify_code_router)
class VerifyCode:
    @verify_code_router.get(
        "/", status_code=status.HTTP_200_OK, name="form"
    )
    def get_form(
            self, request: Request,
            form: OTPCodeForm = Depends(OTPCodeForm.empty)
    ) -> _TemplateResponse:
        content = {"request": request, "form": form.model_dump()}
        return template_obj.TemplateResponse("login.html", content)

    @verify_code_router.post(
        "/", status_code=status.HTTP_303_SEE_OTHER, name="form"
    )
    def send_form(
            self,
            request: Request,
            session: Session = Depends(get_session),
            form: OTPCodeForm = Depends(OTPCodeForm.as_form)
    ) -> RedirectResponse:
        access_token, refresh_token = AuthService(session).authenticate(form)
        response = RedirectResponse(
            url=request.app.url_path_for("PatientAppointment.all"),
            status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 7
        )
        return response

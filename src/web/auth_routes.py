from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv

from web.routes import Prefixes
from service.auth_services import PhoneFormHandler, OTPCode

login_router = APIRouter(prefix=f"{Prefixes.AUTH}/login")
verify_code_router = APIRouter(prefix=f"{Prefixes.AUTH}/verify-code")


@cbv(login_router)
class Login:
    @login_router.get("/", status_code=status.HTTP_200_OK, name="form")
    def get_form(self) -> None:
        pass

    @login_router.post(
        "/", status_code=status.HTTP_303_SEE_OTHER, name="form")
    def send_form(
            self,
            request: Request,
            service: PhoneFormHandler = Depends()) -> RedirectResponse:
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
    def get_form(self) -> None:
        pass

    @verify_code_router.post(
        "/", status_code=status.HTTP_201_CREATED, name="form"
    )
    def send_form(self, otp_code: OTPCode = Depends()) -> None:
        pass

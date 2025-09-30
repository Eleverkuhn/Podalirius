from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv

from service.auth_services import PhoneFormHandler, OTPCode

_base_router = "/auth"
login_router = APIRouter(prefix=f"{_base_router}/login")
verify_code_router = APIRouter(prefix=f"{_base_router}/verify-code")


@cbv(login_router)
class Login:
    @login_router.get("/", status_code=status.HTTP_200_OK, name="login_form")
    def get_login_form(self) -> None:
        pass

    @login_router.post(
        "/", status_code=status.HTTP_303_SEE_OTHER, name="login_form")
    def send_login_form(
            self,
            request: Request,
            service: PhoneFormHandler = Depends()) -> RedirectResponse:
        response = RedirectResponse(
            url=request.app.url_path_for("VerifyCode.verify_code_form"),
            status_code=status.HTTP_303_SEE_OTHER
        )
        return response


@cbv(verify_code_router)
class VerifyCode:
    @verify_code_router.get(
        "/", status_code=status.HTTP_200_OK, name="verify_code_form")
    def get_verify_code_form(self) -> None:
        pass

    @verify_code_router.post(
        "/", status_code=status.HTTP_201_CREATED, name="verify_code_form")
    def send_verify_code_form(self, otp_code: OTPCode = Depends()) -> None:
        pass

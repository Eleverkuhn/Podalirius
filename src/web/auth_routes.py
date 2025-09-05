from fastapi import APIRouter, Form, Depends, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv

from service.auth_services import PhoneFormHandler
from web.routes import Prefixes

login_router = APIRouter(prefix=f"{Prefixes.AUTH}/login")
verify_code_router = APIRouter(prefix=f"{Prefixes.AUTH}/verify-code")


@cbv(login_router)
class Login:
    @login_router.get("/", name="login_form", status_code=status.HTTP_200_OK)
    def get_login_form(self) -> None:
        pass

    @login_router.post("/", name="login_form")
    def send_login_form(
            self,
            phone_form_handler: PhoneFormHandler = Depends()) -> RedirectResponse:
        response = phone_form_handler.response
        return response


@cbv(verify_code_router)
class VerifyCode:
    @verify_code_router.get("/", name="verify_code_form", status_code=status.HTTP_200_OK)
    def get_verify_code_form(self) -> None:
        pass

    @verify_code_router.post("/", name="verify_code_form", status_code=status.HTTP_200_OK)
    def send_verify_code_form(self) -> None:
        pass

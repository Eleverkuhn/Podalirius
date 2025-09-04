from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

_base_router = "/auth"
login_router = APIRouter(prefix=f"{_base_router}/login")
verify_code_router = APIRouter(prefix=f"{_base_router}/verify-code")


@cbv(login_router)
class Login:
    @login_router.get("/", status_code=status.HTTP_200_OK)
    def get_login_form(self) -> None:
        pass

    @login_router.post("/", status_code=status.HTTP_201_CREATED)
    def send_login_form(self) -> None:
        pass


@cbv(verify_code_router)
class VerifyCode:
    @verify_code_router.get("/", status_code=status.HTTP_200_OK)
    def get_verify_code_form(self) -> None:
        pass

    @verify_code_router.post("/", status_code=status.HTTP_201_CREATED)
    def send_verify_code_form(self) -> None:
        pass

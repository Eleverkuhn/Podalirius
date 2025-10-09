import secrets
from datetime import timezone
from datetime import datetime, timedelta

from jose import jwt
from fastapi import Form

from logger.setup import get_logger
from model.patient_models import PatientOuter
from model.form_models import PhoneForm, OTPCodeForm

type Payload = dict[str, bytes | int | datetime]


class JWTTokenService:
    secret = secrets.token_hex(16)
    alg = "HS256"

    def __init__(
            self,
            exp_time: timedelta | None = None
    ) -> None:
        if exp_time:
            self.exp_time = exp_time
        else:
            self.exp_time = timedelta(minutes=1)

    def create_refresh_token(self) -> None:
        pass

    def create_access_token(self, id: int | bytes) -> str:
        payload = self._construct_payload(id)
        return jwt.encode(payload, self.secret, algorithm=self.alg)

    def verify_access_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=[self.alg])
        return payload

    def _construct_payload(self, id: int | bytes) -> Payload:
        """
        Content is whether `patient` bytes UUID or `appointment` integer id
        """
        return {"id": id, "exp": self._set_exp_time()}

    def _set_exp_time(self) -> datetime:
        return datetime.now(timezone.utc) + self.exp_time


class OTPCode:
    def __init__(self, patient: PatientOuter, otp_code: str = Form(...)) -> None:
        self.patient = patient
        self.otp_code = otp_code

    def verify_otp_code(self) -> None:
        pass

    def send_otp_code(self) -> None:
        # TODO: figure out how to send codes via SMS
        pass

    def generate_otp_code(self) -> None:
        # TODO: implement creation of OTP code with Redis
        pass


class PhoneFormHandler:
    def __init__(self, phone: PhoneForm) -> None:
        self.phone = phone

    def get_user_by_phone(self) -> None:
        # TODO: implement retireval of a patient by the given phone number
        pass

    def otp_code_workflow(self) -> None:
        # TODO: consequent process of creating and sending OTP Code to user
        pass


class CodeVerificationFormHandler:
    def __init__(self, otp_code: None | str = Form(...)) -> None:
        self.otp_code = OTPCodeForm(otp_code)

    def set_cookie(self) -> None:
        # TODO: set HTTP Only cookie
        pass

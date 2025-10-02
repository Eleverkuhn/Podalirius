from fastapi import Form

from model.patient_models import PatientOuter
from model.form_models import PhoneForm, OTPCodeForm


class JWTToken:
    def __init__(self) -> None:
        pass

    def create_refresh_token(self) -> None:
        pass

    def create_access_token(self) -> None:
        pass


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

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from jose import jwt
from sqlmodel import Session

from model.form_models import PhoneForm, OTPCodeForm
from model.auth_models import OTPCode
from model.patient_models import PatientOuter
from service.patient_services import PatientService
from data.mysql import get_session
from data.auth_data import OTPCodeRedis

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


class OTPCodeService:
    def __init__(
            self, session: Session, form: PhoneForm | OTPCodeForm) -> None:
        self.session = session
        self.form = form

    @property
    def patient_service(self) -> PatientService:
        return PatientService(self.session)

    @property
    def patient(self) -> PatientOuter | None:
        return self.patient_service._check_patient_exsits(self.form.phone)

    def verify_otp_code(self) -> None:
        pass

    def send_otp_code(self) -> None:
        # TODO: figure out how to send codes via SMS
        pass
    
    def create_otp_code(self) -> None:
        if self.patient:
            OTPCodeRedis().set(self._build_otp_code_model(self.patient.id))
        else:
            patient = self.patient_service.registry(self.form)
            OTPCodeRedis().set(self._build_otp_code_model(patient.id))

    def _build_otp_code_model(self, patient_id: str) -> OTPCode:
        return OTPCode(patient_id=patient_id, value=self._generate_value())

    @staticmethod
    def _generate_value() -> str:
        return str(secrets.randbelow(10**6)).zfill(6)


def post_phone_form(
        session: Session = Depends(get_session),
        form: PhoneForm = Depends(PhoneForm.as_form)
) -> OTPCodeService:
    return OTPCodeService(session, form)

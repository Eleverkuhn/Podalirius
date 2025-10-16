import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlmodel import Session

from exceptions.exc import FormInputError, OTPCodeHashDoesNotMatch
from model.form_models import PhoneForm
from model.auth_models import OTPCode
from service.patient_services import PatientService
from data.auth_data import OTPCodeRedis

type Payload = dict[str, bytes | int | datetime]


class JWTTokenService:
    secret = secrets.token_hex(16)
    alg = "HS256"

    def __init__(
            self, exp_time: timedelta | None = None
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
    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    def patient_service(self) -> PatientService:
        return PatientService(self.session)

    def create(self, phone: str) -> None:
        code = self._generate_code()
        self._send_otp_code(code)
        self._save_otp_code(phone, code)

    def verify(self, form: PhoneForm) -> bool:
        try:
            is_matching = self._hash_matches(form)
        except OTPCodeHashDoesNotMatch:
            raise FormInputError("Verification code does not match")
        else:
            return is_matching

    @staticmethod
    def _generate_code() -> str:
        return str(secrets.randbelow(10**6)).zfill(6)

    def _send_otp_code(self, code: str) -> None:  # INFO: deprecated
        pass

    def _save_otp_code(self, phone: str, code: str) -> None:
        salt, hashed_value = self._hash_otp_code(code)
        otp_code = OTPCode(phone=phone, salt=salt, code=hashed_value)
        OTPCodeRedis().set(otp_code)

    def _hash_otp_code(self, code: str) -> tuple[bytes, bytes]:
        salt = os.urandom(16)
        hashed = self._hash(code, salt)
        return salt, hashed

    def _hash_matches(self, form: PhoneForm) -> bool:
        otp_code_db = OTPCodeRedis().get(form.phone)
        hashed_code = self._hash(form.code, otp_code_db.salt)
        return self._check_hash(hashed_code, otp_code_db.code)

    def _hash(self, value: str, salt: bytes) -> bytes:
        hashed = hashlib.pbkdf2_hmac(
            "sha256", value.encode("utf-8"), salt, 100000
        )
        return hashed

    def _check_hash(self, hashed_code: bytes, db_code: bytes) -> bool:
        if hashed_code == db_code:
            return True
        raise OTPCodeHashDoesNotMatch()

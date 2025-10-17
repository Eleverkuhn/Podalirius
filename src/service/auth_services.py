import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Depends, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from sqlmodel import Session

from exceptions.exc import FormInputError, OTPCodeHashDoesNotMatch
from model.form_models import PhoneForm
from model.auth_models import OTPCode
from model.patient_models import PatientCreate
from service.patient_services import PatientService
from data.auth_data import OTPCodeRedis
from data.mysql import get_session

type Payload = dict[str, bytes | int | datetime]


class AuthService:
    access_exp_time = timedelta(minutes=15)
    refresh_exp_time = timedelta(days=7)

    def __init__(self, session: Session) -> None:
        self.patient_service = PatientService(session)

    def authorize(self, cookies: dict) -> str:
        access_token = self._get_access_token_from_cookie(cookies)
        payload = self._check_access_token_is_expired(access_token)
        patient_id = self._get_patient_id_from_token(payload)
        return patient_id

    def refresh_access_token(self) -> None:
        pass

    def authenticate(self, form: PhoneForm) -> dict[str, str]:
        if OTPCodeService().verify(form):
            patient = self.patient_service._check_patient_exsits(form.phone)
            if not patient:
                patient = self.patient_service.registry(
                    PatientCreate(phone=form.phone)
                )
            return self._create_auth_header(patient.id)

    def _create_auth_header(self, patient_id: str) -> tuple[str, str]:
        return (
            JWTTokenService(self.access_exp_time).create(patient_id),
            JWTTokenService(self.refresh_exp_time).create(patient_id)
        )

    def _get_access_token_from_cookie(self, cookies: dict) -> str:
        token = cookies.get("access_token")
        if token:
            return token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    def _check_access_token_is_expired(self, access_token: str) -> Payload:
        try:
            payload = JWTTokenService().verify(access_token)
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is expired"
            )
        else:
            return payload

    def _get_patient_id_from_token(self, payload: Payload) -> str:
        patient_id = payload.get("id")
        if patient_id:
            return patient_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


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

    def create(self, id: int | bytes | str) -> str:
        payload = self._construct_payload(id)
        return jwt.encode(payload, self.secret, algorithm=self.alg)

    def verify(self, token: str) -> Payload:
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
    def create(self, phone: str) -> None:
        code = self._generate_code()
        self._send_otp_code(code)
        self._save_otp_code(phone, code)

    def verify(self, form: PhoneForm) -> bool:
        try:
            is_matched = self._hash_matches(form)
        except OTPCodeHashDoesNotMatch:
            raise FormInputError("Verification code does not match")
        else:
            return is_matched

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


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)

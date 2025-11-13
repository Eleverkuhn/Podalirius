import hashlib
import secrets
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlmodel import Session

from logger.setup import get_logger
from exceptions.exc import (
    FormInputError,
    OTPCodeHashDoesNotMatch,
    UnauthorizedError,
    AccessTokenExpired
)
from model.form_models import PhoneForm
from model.auth_models import OTPCode
from model.patient_models import PatientCreate, PatientOuter
from service.base_services import BaseService
from data.auth_data import OTPCodeRedis
from data.connections import MySQLConnection

type Payload = dict[str, bytes | int | datetime]


class JWTTokenService:
    secret = secrets.token_hex(16)
    alg = "HS256"

    def __init__(self, exp_delta: timedelta = timedelta(minutes=1)) -> None:
        self.exp_delta = exp_delta

    @property
    def exp_time(self) -> datetime:
        return datetime.now(timezone.utc) + self.exp_delta

    def create(self, id: int | bytes | str) -> str:
        payload = self._construct_payload(id)
        token = jwt.encode(payload, self.secret, algorithm=self.alg)
        return token

    def verify(self, token: str) -> Payload:
        payload = jwt.decode(token, self.secret, algorithms=[self.alg])
        return payload

    def _construct_payload(self, id: int | bytes) -> Payload:
        """
        Content is whether `patient` bytes UUID or `appointment` integer id
        """
        return {"id": id, "exp": self.exp_time}


class AuthService(BaseService):
    access_exp_time = timedelta(minutes=15)
    refresh_exp_time = timedelta(days=7)

    def __init__(self, session: Session, request: Request) -> None:
        super().__init__(session)
        self.cookies = request.cookies

    @property
    def access_token(self) -> str:
        access_token = self.cookies.get("access_token")
        return access_token

    @property
    def refresh_token(self) -> str:
        refresh_token = self.cookies.get("refresh_token")
        return refresh_token

    def refresh_access_token(self, response: RedirectResponse) -> None:
        payload = self._check_refresh_token()
        self._refresh(payload, response)

    def authorize(self) -> str:
        payload = self._get_access_token()
        patient_id = self._get_patient_id(payload)
        return patient_id

    def authenticate(self, form: PhoneForm, response: RedirectResponse) -> None:
        if OTPCodeService().verify(form):
            patient = self._get_patient(form.phone)
            self._set_cookies(patient.id, response)

    def _get_access_token(self) -> Payload:
        if self.access_token:
            payload = self._get_access_token_payload()
            return payload
        raise UnauthorizedError(detail="Not authenticated")

    def _get_access_token_payload(self) -> Payload:
        try:
            payload = JWTTokenService().verify(self.access_token)
        except ExpiredSignatureError:
            raise AccessTokenExpired()
        except JWTError as exc:
            raise UnauthorizedError(detail=str(exc))
        else:
            return payload

    def _check_refresh_token(self) -> Payload:
        if self.refresh_token:
            payload = self._get_refresh_token_payload()
            return payload
        raise UnauthorizedError(detail="Refresh token doesn't exist")

    def _get_refresh_token_payload(self) -> Payload:
        try:
            payload = JWTTokenService().verify(self.refresh_token)
        except ExpiredSignatureError:
            raise UnauthorizedError(detail="Refresh token is expired")
        else:
            return payload

    def _refresh(
            self, refresh_token_payload: Payload, response: RedirectResponse
    ) -> None:
        patient_id = self._get_patient_id(refresh_token_payload)
        new_access_token = self._create_access_token(patient_id)
        self._set_http_only_cookie(
            new_access_token,
            response,
            "access_token",
            self._convert_exp_time(self.access_exp_time)
        )

    def _get_patient_id(self, payload: Payload) -> str:
        patient_id = payload.get("id")
        if patient_id:
            return patient_id
        raise UnauthorizedError(detail="Invalid token")

    def _get_patient(self, phone: str) -> PatientOuter:
        from service.patient_services import PatientService

        service = PatientService(self.session)
        patient = service.check_patient_exists(phone)
        if not patient:
            patient = service.registry(PatientCreate(phone=phone))
        return patient

    def _set_cookies(self, patient_id: str, response: RedirectResponse) -> None:
        access_token, refresh_token = self._create_auth_tokens(patient_id)
        self._set_http_only_cookie(
            access_token,
            response,
            "access_token",
            int(self.access_exp_time.total_seconds())
        )
        self._set_http_only_cookie(
            refresh_token,
            response,
            "refresh_token",
            int(self.refresh_exp_time.total_seconds())
        )

    def _create_auth_tokens(self, patient_id: str) -> tuple[str, str]:
        return (
            self._create_access_token(patient_id),
            self._create_refresh_token(patient_id)
        )

    def _create_access_token(self, patient_id: str) -> str:
        access_token = JWTTokenService(self.access_exp_time).create(patient_id)
        return access_token

    def _create_refresh_token(self, patient_id: str) -> str:
        refresh_token = JWTTokenService(self.refresh_exp_time).create(patient_id)
        return refresh_token

    def _set_http_only_cookie(
            self,
            token: str,
            response: RedirectResponse,
            key: str,
            age: int | float
    ) -> None:
        response.set_cookie(
            key=key,
            value=token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=age
        )

    def _convert_exp_time(self, exp_time: timedelta) -> int:
        exp_time = int(exp_time.total_seconds())
        return exp_time


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
        print(code)  # INFO: For test purposes

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


def get_auth_service(
        request: Request,
        session: Session = Depends(MySQLConnection.get_session)
) -> AuthService:
    return AuthService(session, request)


def authorize(auth: AuthService = Depends(get_auth_service)) -> str:
    patient_id = auth.authorize()
    return patient_id

import os
from datetime import timedelta
from time import sleep

import pytest
from fastapi import HTTPException
from jose.exceptions import ExpiredSignatureError

from logger.setup import get_logger
from exceptions.exc import OTPCodeHashDoesNotMatch
from service.auth_services import AuthService, JWTTokenService, OTPCodeService


@pytest.fixture
def id() -> int:
    return 1


@pytest.fixture
def jwt_token_expired(jwt_token_service: JWTTokenService, id: int) -> str:
    return jwt_token_service.create(id)


@pytest.fixture
def auth_service() -> AuthService:
    return AuthService(None)


@pytest.fixture
def access_token(auth_service: AuthService, id: int) -> str:
    return JWTTokenService(auth_service.access_exp_time).create(id)


class TestAuthService:
    def test_authorize_returns_patient_id(
            self, auth_service: AuthService, access_token: str, id: int
    ) -> None:
        patient_id = auth_service.authorize({"access_token": access_token})
        assert patient_id == id

    def test__create_auth_token(self, uuid_str: str) -> None:
        service = AuthService(None)
        assert service._create_auth_header(uuid_str)

    def test__get_access_token_from_cookie_raises_http_exc(
            self, auth_service: AuthService
    ) -> None:
        with pytest.raises(HTTPException):
            auth_service._get_access_token_from_cookie({"access_token": None})

    @pytest.mark.parametrize(
        "jwt_token_service", [timedelta(seconds=1)], indirect=True
    )
    def test__check_expired_access_token_is_expired_raises_http_exc(
            self, auth_service: AuthService, jwt_token_expired: str
    ) -> None:
        sleep(2)
        with pytest.raises(HTTPException):
            auth_service._check_access_token_is_expired(jwt_token_expired)

    def test__get_patient_id_from_token_raises_http_exc(
            self, auth_service: AuthService
    ) -> None:
        invalid_payload = {"patient_id": None, "sub": None}
        with pytest.raises(HTTPException):
            auth_service._get_patient_id_from_token(invalid_payload)


class TestJWTTokenService:
    def test_create(
            self, jwt_token_service: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service.create(id)
        assert token
        get_logger().debug(token)

    def test_verify(
            self, jwt_token_service: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service.create(id)
        content = jwt_token_service.verify(token)
        assert content.get("id") == id

    @pytest.mark.parametrize(
        "jwt_token_service", [timedelta(seconds=1)], indirect=True
    )
    def test_expired_token_raises_expired_signature_error(
            self, jwt_token_service: JWTTokenService, jwt_token_expired: str
    ) -> None:
        sleep(2)
        with pytest.raises(ExpiredSignatureError):
            jwt_token_service.verify(jwt_token_expired)


class TestOTPCode:
    def test__generate_value(
            self, otp_code_service: OTPCodeService
    ) -> None:
        value = otp_code_service._generate_code()
        assert len(value) == 6

    def test__hash_otp_code(
            self, otp_code_service: OTPCodeService
    ) -> None:
        value = otp_code_service._generate_code()
        salt, hashed_otp_code = otp_code_service._hash_otp_code(value)
        assert salt
        assert hashed_otp_code

    def test__check_hash_raises_does_not_match_error(
            self, otp_code_service: OTPCodeService
    ) -> None:
        rand_bytes_1 = os.urandom(16)
        rand_bytes_2 = os.urandom
        with pytest.raises(OTPCodeHashDoesNotMatch):
            otp_code_service._check_hash(rand_bytes_1, rand_bytes_2)

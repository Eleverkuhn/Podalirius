import os
from datetime import timedelta
from time import sleep

import pytest
from jose.exceptions import ExpiredSignatureError

from logger.setup import get_logger
from exceptions.exc import OTPCodeHashDoesNotMatch
from service.auth_services import JWTTokenService, OTPCodeService


@pytest.fixture
def id() -> int:
    return 1


class TestJWTTokenService:
    def test_create_access_token(
            self, jwt_token_service: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service.create_access_token(id)
        assert token
        get_logger().debug(token)

    def test_verify_access_token(
            self, jwt_token_service: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service.create_access_token(id)
        content = jwt_token_service.verify_access_token(token)
        assert content.get("id") == id

    @pytest.mark.parametrize(
        "jwt_token_service", [timedelta(seconds=1)], indirect=True
    )
    def test_expired_token_raises_expired_signature_error(
            self, jwt_token_service: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service.create_access_token(id)
        sleep(2)
        with pytest.raises(ExpiredSignatureError):
            jwt_token_service.verify_access_token(token)


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

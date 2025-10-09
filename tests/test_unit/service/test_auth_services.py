from datetime import timedelta
from time import sleep

import pytest
from jose.exceptions import ExpiredSignatureError

from logger.setup import get_logger
from service.auth_services import JWTTokenService


@pytest.fixture
def jwt_token_service() -> JWTTokenService:
    return JWTTokenService()


@pytest.fixture
def id() -> int:
    return 1


@pytest.fixture
def jwt_token_service_expired() -> JWTTokenService:
    return JWTTokenService(exp_time=timedelta(seconds=1))


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

    def test_expired_token_raises_expired_signature_error(
            self, jwt_token_service_expired: JWTTokenService, id: int
    ) -> None:
        token = jwt_token_service_expired.create_access_token(id)
        sleep(2)
        with pytest.raises(ExpiredSignatureError):
            jwt_token_service_expired.verify_access_token(token)

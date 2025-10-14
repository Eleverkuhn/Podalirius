import time

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.auth_models import OTPCode
from service.auth_services import OTPCodeService
from data.auth_data import OTPCodeRedis


@pytest.fixture
def otp_code_service(session: Session) -> OTPCodeService:
    return OTPCodeService(session, None)


class TestOTPRedis:
    def test_get_returns_none_if_does_not_exist(  # REF: Maybe remove later
            self, otp_redis: OTPCodeRedis, uuid_bytes: bytes
    ) -> None:
        entry = otp_redis.get(uuid_bytes)
        get_logger().debug(entry)
        assert not entry

    def test_set(
            self, otp_redis: OTPCodeRedis, otp_random: OTPCode
    ) -> None:
        otp_redis.set(otp_random)
        otp_from_db = otp_redis.get(otp_random.value)
        assert otp_from_db == otp_random.patient_id

    @pytest.mark.parametrize("otp_redis", [1], indirect=True)
    def test_token_is_expired(
        seelf, otp_redis: OTPCodeRedis, otp_random: OTPCode
    ) -> None:
        otp_redis.set(otp_random)
        otp_from_db = otp_redis.get(otp_random.value)
        assert otp_from_db
        time.sleep(2)
        otp_from_db_removed = otp_redis.get(otp_random.value)
        assert not otp_from_db_removed

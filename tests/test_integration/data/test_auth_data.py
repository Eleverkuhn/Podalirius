import time

import pytest

from logger.setup import get_logger
from exceptions.exc import OTPCodeNotFound
from model.auth_models import OTPCode
from data.auth_data import OTPCodeRedis


class TestOTPRedis:
    def test_get_raises_otp_code_not_found(
            self, otp_redis: OTPCodeRedis, uuid_bytes: bytes
    ) -> None:
        with pytest.raises(OTPCodeNotFound):
            otp_redis.get(uuid_bytes)

    def test_set(
            self, otp_redis: OTPCodeRedis, otp_random: OTPCode
    ) -> None:
        otp_redis.set(otp_random)
        otp_from_db = otp_redis.get(otp_random.phone)
        assert otp_from_db.model_dump() == otp_random.model_dump()
    
    @pytest.mark.parametrize("otp_redis", [1], indirect=True)
    def test_token_is_expired(
        seelf, otp_redis: OTPCodeRedis, otp_random: OTPCode
    ) -> None:
        otp_redis.set(otp_random)
        otp_from_db = otp_redis.get(otp_random.phone)
        assert otp_from_db
        time.sleep(2)
        with pytest.raises(OTPCodeNotFound):
            otp_redis.get(otp_random.phone)

    def test_delete(
            self, otp_redis: OTPCodeRedis, otp_set_random: OTPCode
    ) -> None:
        otp_from_db = otp_redis.get(otp_set_random.phone)
        assert otp_from_db
        otp_redis.delete(otp_set_random.phone)
        with pytest.raises(OTPCodeNotFound):
            otp_redis.get(otp_set_random.phone)

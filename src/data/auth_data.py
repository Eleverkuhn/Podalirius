from redis import Redis

from model.auth_models import OTPCode
from data.redis_config import redis_conn


class OTPCodeRedis:
    def __init__(self, conn: Redis = redis_conn, lifetime: int = 180) -> None:
        self.conn = conn
        self.lifetime = lifetime
        self.prefix = "otp:"

    def get(self, value: str) -> str:
        return self.conn.get(f"{self.prefix}{value}")

    def set(self, otp: OTPCode) -> None:
        self.conn.set(
            f"{self.prefix}{otp.value}", otp.patient_id, ex=self.lifetime
        )

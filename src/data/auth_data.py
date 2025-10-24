from redis import Redis

from exceptions.exc import OTPCodeNotFound
from model.auth_models import OTPCode
from data.connections import redis_conn


class OTPCodeRedis:
    def __init__(self, conn: Redis = redis_conn, lifetime: int = 180) -> None:
        self.conn = conn
        self.lifetime = lifetime
        self.prefix = "otp:"

    def get(self, phone: str) -> OTPCode:
        otp_code = self.conn.hgetall(f"{self.prefix}{phone}")
        if not otp_code:
            raise OTPCodeNotFound()
        return OTPCode(
            phone=phone, code=otp_code.get(b"code"), salt=otp_code.get(b"salt")
        )

    def set(self, otp: OTPCode) -> None:
        key = f"{self.prefix}{otp.phone}"
        self.conn.hset(key, mapping={"salt": otp.salt, "code": otp.code})
        self.conn.expire(key, self.lifetime)

    def delete(self, phone: str) -> None:
        self.conn.delete(f"{self.prefix}{phone}")

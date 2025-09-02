import pytest
from redis import Redis, AuthenticationError, ConnectionError

from config import Config
from data.redis import redis_conn

settings = Config.get_settings()


class TestRedisConn:
    def test_conn(self) -> None:
        assert redis_conn.ping()

    def test_incorrect_host_raises_conn_err(self) -> None:
        redis_conn = Redis(
            host="wronghost",
            password=settings.redis_password,
            port=settings.redis_port,
            decode_responses=True
        )
        with pytest.raises(ConnectionError):
            redis_conn.ping()

    def test_incorrect_pass_raises_auth_err(self) -> None:
        redis_conn = Redis(
            host=settings.redis_host,
            password="wrongpass",
            port=settings.redis_port,
            decode_responses=True
        )
        with pytest.raises(AuthenticationError):
            redis_conn.ping()

    def test_incorrect_port_raises_conn_err(self) -> None:
        redis_conn = Redis(
            host=settings.redis_host,
            password=settings.redis_password,
            port=6078,
            decode_responses=True
        )
        with pytest.raises(ConnectionError):
            redis_conn.ping()

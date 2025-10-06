import importlib

import pytest
from redis import AuthenticationError, ConnectionError

import config
import data.redis_config as r_conf


class TestRedisConn:
    def reload_imports(self) -> None:
        importlib.reload(config)
        importlib.reload(r_conf)

    def ping_redis_with_error(self, error: Exception) -> None:
        self.reload_imports()
        with pytest.raises(error):
            r_conf.redis_conn.ping()

    def test_conn(self) -> None:
        assert r_conf.redis_conn.ping()

    def test_incorrect_host_raises_conn_err(self, monkeypatch) -> None:
        monkeypatch.setenv("REDIS_HOST", "incorrect_host")
        self.ping_redis_with_error(ConnectionError)

    def test_incorrect_pass_raises_auth_err(self, monkeypatch) -> None:
        monkeypatch.setenv("REDIS_PASSWORD", "incorrect_password")
        self.ping_redis_with_error(AuthenticationError)

    def test_incorrect_port_raises_conn_err(self, monkeypatch) -> None:
        monkeypatch.setenv("REDIS_PORT", "6666")
        self.ping_redis_with_error(ConnectionError)

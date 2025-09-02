import os
import time
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from logger.setup import setup_logging


class _Settings(BaseSettings):
    tz: str
    mysql_root_password: str
    mysql_user: str
    mysql_password: str
    mysql_database: str
    mysql_host: str
    mysql_port: int
    redis_password: str
    redis_host: str
    redis_port: int
    fastapi_host: str
    fastapi_port: int

    model_config = SettingsConfigDict(
        env_file=".env"
    )


class Config:
    _settings = _Settings()

    @classmethod
    @lru_cache
    def get_settings(cls):
        return cls._settings

    @classmethod
    def _set_timezone(cls):
        os.environ["TZ"] = cls._settings.tz
        time.tzset()

    @classmethod
    def setup(cls):
        cls._set_timezone()
        setup_logging()

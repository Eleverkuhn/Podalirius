from redis import Redis

from config import Config

settings = Config.get_settings()

redis_conn = Redis(
    host=settings.redis_host,
    password=settings.redis_password,
    port=settings.redis_port,
    decode_responses=True
)

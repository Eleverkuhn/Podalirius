from redis import Redis
from sqlmodel import Session, create_engine

from config import Config

settings = Config.get_settings()


class MySQLConnection:
    MYSQL_URL = (
        f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
        f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
    )
    engine = create_engine(MYSQL_URL, echo=True)

    @classmethod
    def get_session(cls) -> Session:
        with Session(cls.engine, expire_on_commit=False) as session:
            yield session


redis_conn = Redis(
    host=settings.redis_host,
    password=settings.redis_password,
    port=settings.redis_port,
    decode_responses=False
)

from sqlmodel import Session, create_engine

from config import Config

settings = Config.get_settings()
MYSQL_URL = (
    f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
    f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
)


def get_session() -> Session:
    engine = create_engine(MYSQL_URL, echo=True)
    return Session(engine)

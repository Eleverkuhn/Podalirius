from sqlmodel import Session, create_engine

from config import Config

settings = Config.get_settings()
MYSQL_URL = (
    f"mysql+pymysql://{settings.mysql_user}:{settings.mysql_password}"
    f"@{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}"
)
engine = create_engine(MYSQL_URL, echo=True)


def get_session() -> Session:
    with Session(engine) as session:
        yield session

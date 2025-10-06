import json
import uuid
from pathlib import Path

import pytest
from sqlmodel import Session, SQLModel, Field

from logger.setup import get_logger
from utils import SetUpTest, read_fixture
from data.mysql import get_session, engine
from data.base_sql_models import BaseSQLModel
from data.crud import BaseCRUD


class SQLModelForTest(BaseSQLModel, table=True):
    """
    The distinct sql model for test purposes
    """
    __tablename__ = "test"

    title: str
    year: int = Field(min_length=4, max_length=4)
    description: str | None = Field(default=None)


class SQLModelForTestAlter(BaseSQLModel, table=True):
    __tablename__ = "test_alter"

    title: str
    amount: int


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(get_session())


@pytest.fixture
def crud_test(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTest, SQLModelForTest)


@pytest.fixture
def create_table() -> None:
    SQLModel.metadata.create_all(engine, tables=[
        SQLModelForTest.__table__,
        SQLModelForTestAlter.__table__
    ])


@pytest.fixture
def uuid_bytes() -> bytes:
    return uuid.uuid4().bytes


@pytest.fixture
def setup(session: Session) -> SetUpTest:
    get_logger().debug("inside `setup`")
    return SetUpTest(session)


@pytest.fixture
def fixture_dir() -> Path:
    return Path("tests", "fixtures")


@pytest.fixture
def test_data(fixture_dir: Path, request) -> dict:
    fixture_path = fixture_dir.joinpath(request.param)
    return read_fixture(fixture_path)


@pytest.fixture
def build_test_data(request, test_data) -> BaseSQLModel:
    model, key = request.param
    data = test_data.get(key)
    return model(**data)

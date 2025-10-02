import json
from pathlib import Path

import pytest
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlmodel import Session, inspect

from logger.setup import get_logger
from data.mysql import get_session
from data.base_sql_models import BaseSQLModel


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(get_session())


class SetUp:
    def __init__(self, session: Session) -> None:
        self.session = session

    def load_test_data(self, fixture: Path) -> list[dict]:
        with open(fixture) as file:
            content = json.load(file)
        return content

    def create_entry(self, entry: BaseSQLModel) -> BaseSQLModel:
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def tear_down(self, entry: BaseSQLModel) -> None:
        try:
            self._inspect(entry)
        except ObjectDeletedError:
            pass

    def _inspect(self, entry: BaseSQLModel) -> None:
        try:
            state = inspect(entry)
            if state.persistent:
                self._delete_entry(entry)
        except ObjectDeletedError:
            pass

    def _delete_entry(self, entry: BaseSQLModel) -> None:
        self.session.delete(entry)
        self.session.commit()


@pytest.fixture
def setup(session: Session) -> SetUp:
    get_logger().debug("inside `setup`")
    return SetUp(session)


@pytest.fixture
def fixture_dir() -> Path:
    return Path("tests", "fixtures")


@pytest.fixture
def test_data(setup: SetUp, fixture_dir: Path, request) -> list[dict]:
    fixture_path = fixture_dir.joinpath(request.param)
    return setup.load_test_data(fixture_path)


@pytest.fixture
def build_test_data(request, test_data) -> BaseSQLModel:
    model, key = request.param
    data = test_data.get(key)
    return model(**data)

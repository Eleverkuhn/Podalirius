from typing import Generator

import pytest
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlmodel import Session, inspect

from logger.setup import get_logger
from data.mysql import get_session
from data.base_sql_models import BaseSQLModel

type CreatedTestEntry = Generator[BaseSQLModel, None, None]


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(get_session())


class SetUp:
    def __init__(self, session: Session) -> None:
        self.session = session

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
def build_test_data(request) -> BaseSQLModel:
    get_logger().debug("inside `build_test_data`")
    model, data = request.param
    return model(**data)


@pytest.fixture
def test_entry(setup, build_test_data: BaseSQLModel) -> CreatedTestEntry:
    get_logger().debug("inside test_sentry")
    test_entry = setup.create_entry(build_test_data)
    yield test_entry
    setup.tear_down(test_entry)

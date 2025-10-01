import pytest
from sqlmodel import Session

from data.mysql import get_session


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(get_session())



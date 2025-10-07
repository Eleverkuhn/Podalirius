from typing import Generator

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from data.base_sql_models import BaseSQLModel
from utils import SetUpTest

type CreatedTestEntry = Generator[BaseSQLModel, None, None]


@pytest.fixture
def setup_test(session: Session) -> SetUpTest:  # FIX: why `setup` import from global `conftest` has failed
    return SetUpTest(session)


@pytest.fixture
def test_entry(
        setup_test, request, test_data, build_test_data: BaseSQLModel
) -> CreatedTestEntry:
    """
    Fixture for creating test entries in the database. It either depends on
    parameters passed in a test function to `build_test_data` or on
    parameters passed directly to `test_entry`.
    This separation is needed because some test causes require multiple models.
    """
    get_logger().debug(request)
    if hasattr(request, "param"):
        model, key = request.param
        data = test_data.get(key)
        test_entry = setup_test.create_entry(model(**data))
    else:
        test_entry = setup_test.create_entry(build_test_data)
    yield test_entry
    setup_test.tear_down(test_entry)

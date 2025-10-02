from typing import Generator

import pytest

from data.base_sql_models import BaseSQLModel

type CreatedTestEntry = Generator[BaseSQLModel, None, None]


@pytest.fixture
def test_entry(setup, build_test_data: BaseSQLModel) -> CreatedTestEntry:
    test_entry = setup.create_entry(build_test_data)
    yield test_entry
    setup.tear_down(test_entry)

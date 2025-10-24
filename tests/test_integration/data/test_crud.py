from collections.abc import Generator, Iterator
from pathlib import Path
from time import sleep

import pytest
from sqlalchemy.exc import NoResultFound

from data.base_data import BaseSQLModel, BaseCRUD
from tests.conftest import SQLModelForTest
from utils import SetUpTest, read_fixture

type CreatedTestEntries = Generator[list[SQLModelForTest | None], None, None]


@pytest.fixture
def test_model_data(fixture_dir: Path, request: pytest.FixtureRequest) -> dict:
    data = read_fixture(fixture_dir.joinpath("test_model.json"))
    return data.get(request.param)


@pytest.fixture
def test_model_data_all(fixture_dir: Path) -> dict[str, dict]:
    return read_fixture(fixture_dir.joinpath("test_model.json"))


@pytest.fixture
def test_model(test_model_data: dict) -> SQLModelForTest:
    return SQLModelForTest(**test_model_data)


@pytest.fixture
def test_entry(
        test_model: SQLModelForTest, setup_test: SetUpTest
) -> Iterator[BaseSQLModel]:
    created = setup_test.create_entry(test_model)
    yield created
    setup_test.tear_down(created)


@pytest.fixture
def create_multiple_test_entries(
        setup_test: SetUpTest, test_model_data_all: dict[str, dict]
) -> CreatedTestEntries:
    entries = []
    for model_data in test_model_data_all.values():
        entry = SQLModelForTest(**model_data)
        entry = setup_test.create_entry(entry)
        entries.append(entry)
    yield entries
    for entry in entries:
        setup_test.tear_down(entry)


@pytest.fixture
def update_data() -> dict[str, str]:
    return {
        "title": "updated",
        "description": "title has been updated"
    }


@pytest.mark.parametrize(
    "test_model_data", ["test_1"], indirect=True
)
@pytest.mark.usefixtures("create_table", "test_model_data")
class TestBaseCRUD:
    def test_create_generates_default_values(
            self, crud_test: BaseCRUD, test_model: SQLModelForTest
    ) -> None:
        entry = crud_test.create(test_model)
        assert entry.id
        assert entry.created_at
        assert entry.updated_at

    def test_get_returns_entry(
            self, crud_test: BaseCRUD, test_entry: SQLModelForTest
    ) -> None:
        entry = crud_test._get(test_entry.id)
        assert entry.title == test_entry.title

    def test_get_unexisting_entry(self, crud_test: BaseCRUD) -> None:
        with pytest.raises(NoResultFound):
            crud_test._get(0)
    
    def test_get_all_entries(
            self,
            create_multiple_test_entries: CreatedTestEntries,
            crud_test: BaseCRUD
    ) -> None:
        entries = crud_test.get_all()
        for entry_from_db, created_entry in zip(
                entries, create_multiple_test_entries
        ):
            assert entry_from_db.title == created_entry.title

    def test_get_all_from_empty_db(self, crud_test: BaseCRUD) -> None:
        entries = crud_test.get_all()
        assert entries == []

    def test_update_succeed(
            self,
            test_entry: SQLModelForTest,
            crud_test: BaseCRUD,
            update_data: dict[str, str]
    ) -> None:
        assert not test_entry.title == update_data.get("title")
        crud_test._update(test_entry, update_data)
        assert test_entry.title == update_data.get("title")
        assert test_entry.description == update_data.get("description")

    def test_updated_time_is_updated(
            self,
            test_entry: SQLModelForTest,
            crud_test: BaseCRUD,
            update_data: dict[str, str]
    ) -> None:
        old_update_at = test_entry.updated_at
        sleep(1)
        crud_test._update(test_entry, update_data)
        assert old_update_at < test_entry.updated_at

    def test_delete(
            self,
            test_entry: SQLModelForTest,
            crud_test: BaseCRUD
    ) -> None:
        crud_test._delete(test_entry)
        with pytest.raises(NoResultFound):
            crud_test._get(test_entry.id)

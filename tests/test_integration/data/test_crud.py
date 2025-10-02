from collections.abc import Generator
from time import sleep

import pytest
from sqlalchemy.exc import NoResultFound
from sqlmodel import Field, Session, SQLModel

from logger.setup import get_logger
from data.mysql import engine
from data.crud import BaseCRUD
from data.base_sql_models import BaseSQLModel
from test_integration.conftest import CreatedTestEntry


class SQLModelForTest(BaseSQLModel, table=True):
    """
    The distinct sql model for test purposes
    """
    __tablename__ = "test"

    title: str
    year: int = Field(min_length=4, max_length=4)
    description: str | None = Field(default=None)


type CreatedTestEntries = Generator[list[SQLModelForTest | None], None, None]

test_data = [
    {"title": "test_1", "year": 2025},
    {"title": "test_2", "year": 2025},
    {"title": "test_3", "year": 2025},
    {"title": "test_4", "year": 2025},
    {"title": "test_5", "year": 2025},
]


@pytest.fixture
def create_table() -> None:
    SQLModel.metadata.create_all(engine, tables=[SQLModelForTest.__table__])


@pytest.fixture
def model_data() -> dict:
    return {"title": "test", "year": 2025}


@pytest.fixture
def crud(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTest)


@pytest.fixture
def create_multiple_test_entries(setup) -> CreatedTestEntries:
    entries = []
    for model_data in test_data:
        entry = SQLModelForTest(**model_data)
        entry = setup.create_entry(entry)
        entries.append(entry)
    yield entries
    for entry in entries:
        setup.tear_down(entry)


@pytest.fixture
def update_data() -> dict[str, str]:
    return {
        "title": "updated",
        "description": "title has been updated"
    }


@pytest.mark.usefixtures("create_table")
class TestBaseCRUD:
    @pytest.mark.parametrize(
        "build_test_data", [(SQLModelForTest, test_data[0])], indirect=True
    )
    def test_create_generates_default_values(
            self,
            crud: BaseCRUD,
            build_test_data: SQLModelForTest) -> None:
        entry = crud._create(build_test_data)
        assert entry.id
        assert entry.created_at
        assert entry.updated_at

    @pytest.mark.parametrize(
        "build_test_data", [(SQLModelForTest, test_data[0])], indirect=True
    )
    def test_get_returns_entry(
            self,
            crud: BaseCRUD,
            test_entry: CreatedTestEntry) -> None:
        entry = crud._get(test_entry.id)
        assert entry.title == test_entry.title

    def test_get_unexisting_entry(self, crud: BaseCRUD) -> None:
        with pytest.raises(NoResultFound):
            crud._get(0)
    
    def test_get_all_entries(
            self,
            create_multiple_test_entries: CreatedTestEntries,
            crud: BaseCRUD) -> None:
        entries = crud._get_all()
        for entry_from_db, created_entry in zip(
                entries, create_multiple_test_entries
        ):
            assert entry_from_db.title == created_entry.title

    def test_get_all_from_empty_db(self, crud: BaseCRUD) -> None:
        entries = crud._get_all()
        assert entries == []

    @pytest.mark.parametrize(
        "build_test_data", [(SQLModelForTest, test_data[0])], indirect=True
    )
    def test_update_succeed(
            self,
            test_entry: CreatedTestEntry,
            crud: BaseCRUD,
            update_data: dict[str, str]) -> None:
        crud._update(test_entry, update_data)
        assert test_entry.title == update_data.get("title")
        assert test_entry.description == update_data.get("description")

    @pytest.mark.parametrize(
        "build_test_data", [(SQLModelForTest, test_data[0])], indirect=True
    )
    def test_updated_time_is_updated(
            self,
            test_entry: CreatedTestEntry,
            crud: BaseCRUD,
            update_data: dict[str, str]) -> None:
        old_update_at = test_entry.updated_at
        sleep(1)
        crud._update(test_entry, update_data)
        assert old_update_at < test_entry.updated_at

    @pytest.mark.parametrize(
        "build_test_data", [(SQLModelForTest, test_data[0])], indirect=True
    )
    def test_delete(
            self,
            test_entry: CreatedTestEntry,
            crud: BaseCRUD) -> None:
        crud._delete(test_entry)
        with pytest.raises(NoResultFound):
            crud._get(test_entry.id)

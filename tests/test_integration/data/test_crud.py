from collections.abc import Generator
from time import sleep

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlmodel import Field, Session, SQLModel, inspect

from logger.setup import get_logger
from data.mysql import engine
from data.crud import BaseCRUD
from data.base_sql_models import BaseSQLModel


class SQLModelForTest(BaseSQLModel, table=True):
    """
    The distinct sql model for test purposes
    """
    __tablename__ = "test"

    title: str
    year: int = Field(min_length=4, max_length=4)
    description: str | None = Field(default=None)


type CreatedTestEntry = Generator[BaseSQLModel, None, None]
type CreatedTestEntries = Generator[list[SQLModelForTest | None], None, None]

test_data = [
    {"title": "test_1", "year": 2025},
    {"title": "test_2", "year": 2025},
    {"title": "test_3", "year": 2025},
    {"title": "test_4", "year": 2025},
    {"title": "test_5", "year": 2025},
]


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
    return SetUp(session)


@pytest.fixture
def create_table() -> None:
    SQLModel.metadata.create_all(engine, tables=[SQLModelForTest.__table__])


@pytest.fixture
def model_data() -> dict:
    return {"title": "test", "year": 2025}


@pytest.fixture
def model_for_test(request) -> SQLModelForTest:
    model_data = request.param
    return SQLModelForTest(**model_data)


@pytest.fixture
def crud(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTest)


@pytest.fixture
def create_test_entry(
        setup: SetUp,
        model_for_test: SQLModelForTest) -> CreatedTestEntry:
    test_entry = setup.create_entry(model_for_test)
    yield test_entry
    setup.tear_down(test_entry)


@pytest.fixture
def create_multiple_test_entries(
        setup: SetUp) -> CreatedTestEntries:
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
        "model_for_test", [test_data[0]], indirect=True
    )
    def test_add_generates_default_values(
            self,
            crud: BaseCRUD,
            model_for_test: SQLModelForTest) -> None:
        entry = crud.add(model_for_test)
        assert entry.id
        assert entry.created_at
        assert entry.updated_at

    @pytest.mark.parametrize(
        "model_for_test", [test_data[0]], indirect=True
    )
    def test_get_returns_entry(
            self,
            crud: BaseCRUD,
            create_test_entry: CreatedTestEntry) -> None:
        entry = crud.get(create_test_entry.id)
        assert entry.title == create_test_entry.title

    def test_get_unexisting_entry(self, crud: BaseCRUD) -> None:
        with pytest.raises(NoResultFound):
            crud.get(0)
    
    def test_get_all_entries(
            self,
            create_multiple_test_entries: CreatedTestEntries,
            crud: BaseCRUD) -> None:
        entries = crud.get_all()
        for entry_from_db, created_entry in zip(
                entries, create_multiple_test_entries
        ):
            assert entry_from_db.title == created_entry.title

    def test_get_all_from_empty_db(self, crud: BaseCRUD) -> None:
        entries = crud.get_all()
        assert entries == []

    @pytest.mark.parametrize(
        "model_for_test", [test_data[0]], indirect=True
    )
    def test_update_succeed(
            self,
            create_test_entry: CreatedTestEntry,
            crud: BaseCRUD,
            update_data: dict[str, str]) -> None:
        crud.update(create_test_entry, update_data)
        assert create_test_entry.title == update_data.get("title")
        assert create_test_entry.description == update_data.get("description")

    @pytest.mark.parametrize(
        "model_for_test", [test_data[0]], indirect=True
    )
    def test_updated_time_is_updated(
            self,
            create_test_entry: CreatedTestEntry,
            crud: BaseCRUD,
            update_data: dict[str, str]) -> None:
        old_update_at = create_test_entry.updated_at
        sleep(1)
        crud.update(create_test_entry, update_data)
        assert old_update_at < create_test_entry.updated_at

    @pytest.mark.parametrize(
        "model_for_test", [test_data[0]], indirect=True
    )
    def test_delete(
            self,
            create_test_entry: CreatedTestEntry,
            crud: BaseCRUD) -> None:
        crud.delete(create_test_entry)
        with pytest.raises(NoResultFound):
            crud.get(create_test_entry.id)

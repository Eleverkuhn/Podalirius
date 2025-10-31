import base64
from pathlib import Path

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from utils import DatabaseSeeder, SetUpTest, read_fixture
from data.base_data import BaseSQLModel, BaseCRUD
from data.sql_models import Patient
from tests.conftest import SQLModelForTest, SQLModelForTestAlter, SetUpTest


@pytest.fixture
def models_to_fixtures() -> dict[type[BaseSQLModel], Path]:
    dir = Path(__file__).parent.parent.joinpath("fixtures")
    return {
        SQLModelForTest: dir.joinpath("test_model.json"),
        SQLModelForTestAlter: dir.joinpath("test_model_alter.json")
    }


@pytest.fixture
def db_seeder(
        session: Session, models_to_fixtures: dict[type[BaseSQLModel], Path]
) -> DatabaseSeeder:
    return DatabaseSeeder(session, models_to_fixtures)


@pytest.fixture
def fixture_content_test() -> dict:
    return {
        "test_1": {
            "title": "example1",
            "year": 2025,
        },
        "test_2": {
            "title": "example2",
            "year": 2010,
            "description": "Example description"
        },
        "test_3": {
            "title": "example3",
            "year": 2021,
        },
    }


@pytest.fixture
def fixture_dir() -> Path:
    return Path("src", "data", "sql", "fixtures")


@pytest.fixture
def crud_test_alter(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTestAlter, SQLModelForTestAlter)


@pytest.fixture
def patients_data(fixture_dir: Path, request: pytest.FixtureRequest) -> dict:
    data = read_fixture(fixture_dir.joinpath("patients.json"))
    return data[request.param]


@pytest.mark.usefixtures("create_table")
class TestDatabaseSeeder:
    def test_execute(
            self,
            db_seeder: DatabaseSeeder,
            crud_test: BaseCRUD,
            crud_test_alter: BaseCRUD,
            setup_test: SetUpTest
    ) -> None:
        assert crud_test.get_all() == []
        assert crud_test_alter.get_all() == []
        db_seeder.execute()
        setup_test.delete_multiple(crud_test.get_all())
        setup_test.delete_multiple(crud_test_alter.get_all())

    @pytest.mark.skip()
    def test__populate_table_test(
            self,
            db_seeder: DatabaseSeeder,
            crud_test: BaseCRUD,
            fixture_content_test: dict,
            setup_test: SetUpTest
    ) -> None:
        assert crud_test.get_all() == []
        single = fixture_content_test.get("test_1")
        db_seeder._populate_table(single)
        entries = crud_test.get_all()
        assert entries[0].title == single.get("title")
        setup_test.delete_multiple(entries)

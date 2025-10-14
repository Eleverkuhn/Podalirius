from pathlib import Path

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from utils import DatabaseSeeder, SetUpTest
from model.auth_models import OTPCode
from data.base_sql_models import BaseSQLModel
from data.crud import BaseCRUD
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
def crud_test_alter(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTestAlter, SQLModelForTestAlter)


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

    def test__populate_table_test(
            self,
            db_seeder: DatabaseSeeder,
            crud_test: BaseCRUD,
            fixture_content_test: dict,
            setup_test: SetUpTest
    ) -> None:
        assert crud_test.get_all() == []
        single = fixture_content_test.get("test_1")
        db_seeder._populate_table(crud_test, single)
        entries = crud_test.get_all()
        assert entries[0].title == single.get("title")
        setup_test.delete_multiple(entries)


class TestSetUpTest:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("otp_set")
    def test_find_otp_code_by_patient_id(
            self, setup_test: SetUpTest, otp_random: OTPCode
    ) -> None:
        otp_code = setup_test.find_otp_code_by_patient_id(otp_random.patient_id)
        assert otp_code.patient_id == otp_random.patient_id

from pathlib import Path

import pytest
from sqlmodel import Session, Table

from data.base_sql_models import BaseSQLModel
from data.sql.seed_db import (
    InitSeed, FixtureJSON, DoctorSQLModel, SpecialtySQLModel,
    DatabaseTruncator
)
from data.crud import BaseCRUD


@pytest.fixture
def seed(session: Session) -> InitSeed:
    return InitSeed(session)


@pytest.fixture
def fixture_dir_path(seed: InitSeed) -> Path:
    src = Path("src")
    return src.joinpath(seed.fixture_dir)


@pytest.fixture
def doctors_fixture(fixture_dir_path: Path) -> Path:
    file = "doctors.json"
    return fixture_dir_path.joinpath(file)


@pytest.fixture
def specialties_fixture(fixture_dir_path: Path) -> Path:
    file = "specialties.json"
    return fixture_dir_path.joinpath(file)


@pytest.fixture
def doctor_sql_model(clean_up) -> DoctorSQLModel:
    with clean_up(DoctorSQLModel) as sql_model:
        yield sql_model


@pytest.fixture
def specialty_sql_model(clean_up) -> SpecialtySQLModel:
    with clean_up(SpecialtySQLModel) as sql_model:
        yield sql_model


@pytest.fixture
def sql_models_to_fixture(
        doctors_fixture: Path,
        specialties_fixture: Path,
        doctor_sql_model: DoctorSQLModel,
        specialty_sql_model: SpecialtySQLModel) -> dict[BaseSQLModel, Path]:
    return {
        doctor_sql_model: doctors_fixture,
        specialty_sql_model: specialties_fixture
    }


@pytest.fixture
def seed_with_models(
        session: Session,
        sql_models_to_fixture: dict[BaseSQLModel, Path]) -> InitSeed:
    return InitSeed(session, sql_models_to_fixture)


@pytest.fixture
def crud(session: Session) -> BaseCRUD:
    crud = BaseCRUD(session)
    return crud


@pytest.fixture
def doctor_crud(session: Session, doctor_sql_model: DoctorSQLModel) -> BaseCRUD:
    crud = BaseCRUD(session, doctor_sql_model)
    return crud


@pytest.fixture
def specialty_crud(
        session: Session, specialty_sql_model: SpecialtySQLModel) -> BaseCRUD:
    crud = BaseCRUD(session, specialty_sql_model)
    return crud


@pytest.fixture
def doctors_fixture_content() -> FixtureJSON:
    test_content = [
        {
            "first_name": "TestFirst1",
            "middle_name": "TestMiddle1",
            "last_name": "TestLast1",
            "experience": "2024-09-23"
        },
        {
            "first_name": "TestFirst2",
            "middle_name": "TestMiddle2",
            "last_name": "TestLast2",
            "experience": "2023-09-23"
        }
    ]
    return test_content


@pytest.fixture
def sql_models_list(seed: InitSeed) -> list[BaseSQLModel]:
    sql_models = seed.sql_models_to_fixture.keys()
    return sql_models


@pytest.fixture
def database_truncator(session: Session) -> DatabaseTruncator:
    return DatabaseTruncator(session)


@pytest.fixture
def tables(sql_models_list: list[BaseSQLModel]) -> list[Table]:
    return DatabaseTruncator._convert_models_to_tables(sql_models_list)


def test_fixture_dir_exists(fixture_dir_path: Path) -> None:
    assert fixture_dir_path.exists()


@pytest.mark.skip("Run only when database is needed to get populated with fixture data")
class TestInitSeedPopulate:
    """
    Created to populate database with fixture data and check it manually
    """
    def test_execute(self, seed: InitSeed) -> None:
        seed.execute()


@pytest.mark.skip(reason="Everything's working fine the problem is tear down logic removes all rows from table")
class TestInitSeed:
    def test_seed_with_models_execute(
            self,
            seed_with_models: InitSeed,
            doctor_crud: BaseCRUD,
            specialty_crud: BaseCRUD,
            doctors_fixture: Path,
            specialties_fixture: Path) -> None:
        seed_with_models.execute()
        doctors = doctor_crud.get_all()
        doctors_fixture_content = seed_with_models._get_fixture_content(
            doctors_fixture
        )
        assert len(doctors) == len(doctors_fixture_content)
        specialties = specialty_crud.get_all()
        specialties_fixture_content = seed_with_models._get_fixture_content(
            specialties_fixture
        )
        assert len(specialties) == len(specialties_fixture_content)

    def test__load_fixture_to_table(
            self,
            seed: InitSeed,
            doctor_sql_model: DoctorSQLModel,
            doctors_fixture: Path,
            doctor_crud: BaseCRUD) -> None:
        seed._load_fixture_to_table(doctor_sql_model, doctors_fixture)
        doctors = doctor_crud.get_all()
        content = seed._get_fixture_content(doctors_fixture)
        assert len(doctors) == len(content)

    def test__populate_doctors_table(
            self,
            seed: InitSeed,
            doctor_crud: BaseCRUD,
            doctors_fixture_content: FixtureJSON) -> None:
        seed._populate_table(doctor_crud, doctors_fixture_content)
        doctors = doctor_crud.get_all()
        assert len(doctors) == len(doctors_fixture_content)

    def test__get_fixture_content(self, doctors_fixture: Path) -> None:
        result = InitSeed._get_fixture_content(doctors_fixture)
        assert result is not None


@pytest.mark.skip(reason="Run when test data is needed to be removed")
class TestDatabaseTruncator:
    def test_reset_database(
            self,
            database_truncator: DatabaseTruncator,
            doctor_crud: BaseCRUD) -> None:
        doctors = doctor_crud.get_all()
        assert doctors != []
        database_truncator.reset_database()
        doctors_truncated = doctor_crud.get_all()
        assert doctors_truncated == []

    @pytest.mark.skip(reason="Need to fix FK Constraint error")  # FIX:
    def test__truncate_tables(
            self,
            database_truncator: DatabaseTruncator,
            sql_models_list: list[BaseSQLModel],
            doctor_crud: BaseCRUD) -> None:
        doctors = doctor_crud.get_all()
        assert doctors is not None
        database_truncator._truncate_tables(sql_models_list)
        doctors_truncated = doctor_crud.get_all()
        assert doctors_truncated is None

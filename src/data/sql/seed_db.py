import json
from datetime import date, time
from decimal import Decimal
from typing import override
from pathlib import Path

from sqlalchemy import TextClause
from sqlmodel import Field, Session, SQLModel, Enum, Table, text

from model.base_models import BaseModel
from data.base_sql_models import BaseSQLModel, BaseEnumSQLModel, PersonSQLModel
from data.appointment_data import DoctorSQLModel
from data.crud import BaseCRUD

type FixtureJSON = list[dict[str, str]]

SERVICE_TITLE_MAX_LENGHT = 75
PRECISION = 8
SCALE = 2


class SpecialtySQLModel(BaseSQLModel, table=True):
    __tablename__ = "specialties"

    title: str = Field(max_length=30)
    description: None | str = Field(default=None)


class ServiceTypeSQLModel(BaseSQLModel, table=True):
    __tablename__ = "services_types"

    title: str = Field(max_length=SERVICE_TITLE_MAX_LENGHT)
    price: Decimal = Field(max_digits=PRECISION, decimal_places=SCALE)


class ServiceSQLModel(BaseSQLModel, table=True):
    __tablename__ = "services"

    title: str = Field(max_length=SERVICE_TITLE_MAX_LENGHT)
    description: None | str = Field(default=None)
    markup: None | Decimal = Field(
        default=0, max_digits=PRECISION, decimal_places=SCALE
    )

    type_id: int = Field(foreign_key="services_types.id")


class Weekday(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class WorkScheduleSQLModel(BaseEnumSQLModel, table=True):
    __tablename__ = "work_schedules"

    weekday: Weekday
    start_time: time
    end_time: time

    doctor_id: int = Field(foreign_key="doctors.id")


class ServiceToSpecialty(BaseSQLModel, table=True):
    __tablename__ = "services_to_specialties"

    service_id: int = Field(foreign_key="services.id")
    specialty_id: int | None = Field(
        default=None,
        foreign_key="specialties.id"
    )


class SpecialtyToDoctor(BaseSQLModel, table=True):
    __tablename__ = "specialties_to_doctors"

    doctor_id: int = Field(foreign_key="doctors.id")
    specialty_id: int = Field(foreign_key="specialties.id")


class ServiceToDoctor(BaseSQLModel, table=True):
    __tablename__ = "services_to_doctors"

    markup: None | Decimal = Field(
        default=0, max_digits=PRECISION, decimal_places=SCALE
    )

    doctor_id: int = Field(foreign_key="doctors.id")
    service_id: int = Field(foreign_key="services.id")


# class ServiceToAppointment(BaseSQLModel, table=True):
#     __tablename__ = "services_to_appointments"
# 
#     appointment_id: int = Field(foreign_key="appoitments.id")
#     service_id: int = Field(foreign_key="services.id")


class DoctorCRUD(BaseCRUD):
    @override
    def __init__(
        self,
            session: Session,
            sql_model: DoctorSQLModel = DoctorSQLModel,
            return_model: BaseModel | None = None) -> None:
        super().__init__(session, sql_model, return_model)


class InitSeed:
    fixture_dir = Path(__file__).parent.joinpath("fixtures")

    def __init__(
            self,
            session: Session,
            sql_models_to_fixture: dict[BaseSQLModel, Path] | None = None
    ) -> None:
        if sql_models_to_fixture:
            self.sql_models_to_fixture = sql_models_to_fixture
        self.sql_models_to_fixture = {
            DoctorSQLModel: self.fixture_dir.joinpath("doctors.json"),
            WorkScheduleSQLModel: self.fixture_dir.joinpath("work_schedules.json"),
            ServiceTypeSQLModel: self.fixture_dir.joinpath("services_types.json"),
            ServiceSQLModel: self.fixture_dir.joinpath("services.json"),
            SpecialtySQLModel: self.fixture_dir.joinpath("specialties.json"),
            ServiceToSpecialty: self.fixture_dir.joinpath("services_to_specialties.json"),
            SpecialtyToDoctor: self.fixture_dir.joinpath("specialties_to_doctors.json"),
            ServiceToDoctor: self.fixture_dir.joinpath("services_to_doctors.json")
        }
        self.session = session

    def execute(self) -> None:
        for sql_model, fixture in self.sql_models_to_fixture.items():
            self._load_fixture_to_table(sql_model, fixture)

    def _load_fixture_to_table(
            self, sql_model: SQLModel, fixture: Path) -> None:
        content = self._get_fixture_content(fixture)
        crud = self._get_crud(sql_model)
        self._populate_table(crud, content)

    @staticmethod
    def _get_fixture_content(fixture: Path) -> FixtureJSON:
        with open(fixture) as file:
            content = json.load(file)
        return content

    def _get_crud(self, sql_model: SQLModel) -> BaseCRUD:
        crud = BaseCRUD(session=self.session, sql_model=sql_model, return_model=sql_model)
        return crud

    def _populate_table(self, crud: BaseCRUD, content: FixtureJSON,) -> None:
        for row in content:
            instance = crud.sql_model(**row)
            crud.create(instance)
            crud.session.commit()


class DatabaseTruncator:
    _set_fk_0: TextClause = text("SET FOREIGN_KEY_CHECKS = 0;")
    _set_fk_1: TextClause = text("SET FOREIGN_KEY_CHECKS = 1;")  # TODO: this can be refactored

    def __init__(self, session: Session) -> None:
        self.session = session

    def reset_database(self) -> None:
        self.session.exec(self._set_fk_0)
        self._truncate_tables()
        self.session.exec(self._set_fk_1)

    def _truncate_tables(self) -> None:
        for table in reversed(BaseSQLModel.metadata.sorted_tables):
            statement = self._get_truncate_table_query_string(table)
            self.session.exec(text(statement))

    @staticmethod
    def _get_truncate_table_query_string(table: Table) -> TextClause:
        return text(f"TRUNCATE TABLE `{table.name}`;")

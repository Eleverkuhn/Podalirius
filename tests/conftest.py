import uuid
from pathlib import Path

import pytest
from fastapi import Response
from sqlmodel import Session, SQLModel, Field

from logger.setup import get_logger
from utils import SetUpTest, read_fixture
from model.form_models import AppointmentBookingForm, PhoneForm, OTPCodeForm
from service.auth_services import JWTTokenService, OTPCodeService
from data.connections import MySQLConnection
from data.base_data import BaseSQLModel, BaseCRUD
from data.patient_data import PatientSQLModel


class SQLModelForTest(BaseSQLModel, table=True):
    """
    The distinct sql model for test purposes
    """
    __tablename__ = "test"

    title: str
    year: int = Field(min_length=4, max_length=4)
    description: str | None = Field(default=None)


class SQLModelForTestAlter(BaseSQLModel, table=True):
    __tablename__ = "test_alter"

    title: str
    amount: int


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(MySQLConnection.get_session())


@pytest.fixture
def crud_test(session: Session) -> BaseCRUD:
    return BaseCRUD(session, SQLModelForTest, SQLModelForTest)


@pytest.fixture
def create_table() -> None:
    SQLModel.metadata.create_all(MySQLConnection.engine, tables=[
        SQLModelForTest.__table__,
        SQLModelForTestAlter.__table__
    ])


@pytest.fixture
def uuid_bytes() -> bytes:
    return uuid.uuid4().bytes


@pytest.fixture
def uuid_str() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def setup_test(session: Session) -> SetUpTest:
    return SetUpTest(session)


@pytest.fixture
def fixture_dir() -> Path:
    return Path("tests", "fixtures")


@pytest.fixture
def patients_data(fixture_dir: Path, request: pytest.FixtureRequest) -> dict:
    data = read_fixture(fixture_dir.joinpath("test_patients.json"))
    return data.get(request.param)


@pytest.fixture
def patient_sql_model(patients_data: dict) -> PatientSQLModel:
    return PatientSQLModel(**patients_data)


@pytest.fixture
def appointments_data(
        fixture_dir: Path, request: pytest.FixtureRequest
) -> dict:
    data = read_fixture(fixture_dir.joinpath("test_appointments.json"))
    return data.get(request.param)


@pytest.fixture
def appointment_booking_form(appointments_data: dict) -> AppointmentBookingForm:
    return AppointmentBookingForm(**appointments_data)


@pytest.fixture
def jwt_token_service(request: pytest.FixtureRequest) -> JWTTokenService:
    if hasattr(request, "param"):
        service = JWTTokenService(request.param)
    else:
        service = JWTTokenService()
    return service


@pytest.fixture
def phone_form(patients_data: dict) -> PhoneForm:
    return PhoneForm(phone=patients_data.get("phone"))


@pytest.fixture
def otp_code_form(patients_data: dict) -> OTPCodeForm:
    return OTPCodeForm(
        phone=patients_data.get("phone"),
        code="123456"
    )


@pytest.fixture
def otp_code_service() -> OTPCodeService:
    return OTPCodeService()


@pytest.fixture
def mock_response() -> Response:
    return Response()

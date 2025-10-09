from datetime import timedelta

from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from service.auth_services import JWTTokenService
from service.appointment_services import AppointmentJWTTokenService
from data import sql_models
from data.base_sql_models import BaseSQLModel
from data.patient_data import PatientSQLModel
from utils import SetUpTest, read_fixture

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


@pytest.fixture  # REF: merge  this class and the below
def patient(
        fixture_dir: Path, setup_test: SetUpTest, request
) -> PatientSQLModel:
    data = read_fixture(fixture_dir.joinpath("test_patients.json"))
    patient_data = data.get(request.param)
    entry = setup_test.create_entry(PatientSQLModel(**patient_data))
    yield entry
    setup_test.tear_down(entry)


@pytest.fixture
def appointment(
        fixture_dir: Path,
        setup_test: SetUpTest,
        patient: PatientSQLModel,
        request
) -> sql_models.Appointment:
    data = read_fixture(fixture_dir.joinpath("test_appointments.json"))
    appointment_data = data.get(request.param)
    entry = setup_test.create_entry(
        sql_models.Appointment(**appointment_data, patient_id=patient.id)
    )
    yield entry
    setup_test.tear_down(entry)


@pytest.fixture
def jwt_token_appointment(
        request, appointment: sql_models.Appointment
) -> str:
    return JWTTokenService(request.param).create_access_token(appointment.id)


@pytest.fixture
def appointment_token_service(session: Session) -> AppointmentJWTTokenService:
    return AppointmentJWTTokenService(session)


@pytest.fixture
def jwt_token_service_expired() -> JWTTokenService:
    return JWTTokenService(exp_time=timedelta(seconds=1))

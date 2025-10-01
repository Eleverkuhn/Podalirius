import uuid
from contextlib import contextmanager
from datetime import date, datetime

import pytest
import sqlalchemy
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, select

from main import app
from model.patient_models import PatientCreate
from service.appointment_services import (
    AppointmentBooking,
    get_appointment_booking
)

from data.mysql import get_session
from data.patient_data import PatientSQLModel, PatientCRUD


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def session() -> Session:
    return next(get_session())


@pytest.fixture
def today() -> datetime:
    return datetime.now()


@pytest.fixture
def phone_number() -> str:
    return "7887710200"


@pytest.fixture
def birth_date_from_json() -> str:
    return "1997-09-03"


@pytest.fixture
def birth_date_converted(birth_date_from_json: str) -> date:
    return date.fromisoformat(birth_date_from_json)


@pytest.fixture
def patient_create_data(
        phone_number: str,
        birth_date_converted: date) -> PatientCreate:
    return PatientCreate(
        last_name="lastname",
        middle_name="middlename",
        first_name="firstname",
        phone=phone_number,
        birth_date=birth_date_converted
    )
        # birth_date=datetime.fromisoformat(birth_date_from_json))


@pytest.fixture
def patient_update_data() -> dict[str, str]:
    return {
        "last_name": "lastnameupdated",
        # "updated_at": datetime.now() + timedelta(minutes=5)
    }


@pytest.fixture
def cleanup_created_entries(session: Session) -> list[SQLModel | None]:
    created = []
    yield created
    for entry in created:
        session.delete(entry)
    session.commit()


@pytest.fixture
def create_test_patient(
        session: Session,
        patient_create_data: PatientCreate,
        cleanup_created_entries: list[None | PatientSQLModel]) -> PatientSQLModel:
    # TODO: probably need to refactor this
    test_patient = PatientSQLModel(**patient_create_data.model_dump())
    session.add(test_patient)
    session.commit()
    session.refresh(test_patient)
    cleanup_created_entries.append(test_patient)
    return test_patient


@pytest.fixture
def clean_up(session: Session):
    @contextmanager
    def _clean(sql_model: SQLModel):
        yield sql_model

        statement = select(sql_model)
        entries = session.exec(statement)
        if entries:
            for entry in entries:
                session.delete(entry)
            session.commit()

    return _clean


@pytest.fixture
def uuid_bytes() -> bytes:
    return uuid.uuid4().bytes


@pytest.fixture
def uuid_str() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def patient_uuid_str(
        create_test_patient: PatientSQLModel) -> str:
    return PatientCRUD.uuid_to_str(create_test_patient.id)


@pytest.fixture
def unlogged_in_user() -> AppointmentBooking:  # TODO: probably need to move this to `test_appointment_services`
    return get_appointment_booking()


@pytest.fixture
def unmatching_patient_create_data(
        patient_create_data: PatientCreate,
        patient_update_data: dict[str, str]) -> PatientCreate:
    dumped = patient_create_data.model_dump()
    dumped.update(patient_update_data)
    updated_patient_create_data = PatientCreate(**dumped)
    return updated_patient_create_data

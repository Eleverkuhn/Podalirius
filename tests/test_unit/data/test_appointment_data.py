from datetime import datetime

import pytest
from sqlmodel import Session

from model.appointment_models import AppointmentCreate
from data.appointment_data import AppointmentCrud, Status
from data.patient_data import PatientSQLModel


@pytest.fixture
def today() -> datetime:
    return datetime.now().replace(microsecond=0)


@pytest.fixture
def pending_status() -> str:
    return Status.PENDING


@pytest.fixture
def appointment(
        create_test_patient: PatientSQLModel,
        today: datetime,
        pending_status: str) -> AppointmentCreate:
    """
    Test patient is created in this fixture so don't need to create
    an additional one in tests
    """
    appointment = AppointmentCreate(
        doctor_id=1,
        patient_id=create_test_patient.id,
        date=today,
        status=pending_status
    )
    return appointment


@pytest.fixture
def appointment_data(appointment: AppointmentCreate) -> dict:
    return appointment.model_dump()


@pytest.fixture
def appointment_crud(session: Session) -> AppointmentCrud:
    crud = AppointmentCrud(session)
    return crud


class TestAppointmentCrud:
    def test_create(
            self,
            appointment_data: dict,
            appointment_crud: AppointmentCrud) -> None:
        created_appointment = appointment_crud.create(
            appointment_data
        )
        dumped_created_appointment = created_appointment.model_dump(
            exclude={"id"}
        )
        assert dumped_created_appointment == appointment_data

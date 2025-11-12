from datetime import date, time

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from service.form_services import (
    AppointmentBookingFormDataConstructor,
    AppointmentRescheduleFormDataConstructor
)
from data.sql_models import Doctor
from data.appointment_data import AppointmentCRUD
from tests.test_integration.conftest import (
    BasePatientTest, BaseDoctorTest, MockRequest
)


@pytest.fixture
def appointment_crud(session: Session) -> AppointmentCRUD:
    crud = AppointmentCRUD(session)
    return crud


@pytest.fixture
def get_doctor_appointments_expected_result(
        appointment_crud: AppointmentCRUD, doctor: Doctor
) -> set[tuple[date, time]]:
    appointments = appointment_crud.get_all_by_doctor(doctor.id)
    appointment_times = {
        (appointment.date, appointment.time)
        for appointment
        in appointments
        if appointment.status == "pending"
    }
    return appointment_times


class TestAppointmentBookingFormDataConstructor(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _constructor(self, session: Session, mock_request: MockRequest) -> None:
        self.constructor = AppointmentBookingFormDataConstructor(
            session, mock_request
        )

    def test_construct(self) -> None:
        content = self.constructor.exec()
        assert content


class TestAppointmentRescheduleFormDataConstructor(BaseDoctorTest):
    @pytest.fixture(autouse=True)
    def _constructor(self, session: Session, doctor: Doctor) -> None:
        self.constructor = AppointmentRescheduleFormDataConstructor(
            session, doctor.id
        )

    def test_exec(self) -> None:
        appointment_schedule = self.constructor.exec()
        assert appointment_schedule
        get_logger().debug(f"Appointment schedule: {appointment_schedule}")

    def test__get_doctor_appointments(
        self, get_doctor_appointments_expected_result: set[tuple[date, time]]
    ) -> None:
        appointments = self.constructor._get_doctor_appointments()
        assert appointments == get_doctor_appointments_expected_result

    def test__get_doctor_schedule(self) -> None:
        doctor_schedule = self.constructor._get_doctor_schedule()
        assert doctor_schedule
        get_logger().debug(doctor_schedule)

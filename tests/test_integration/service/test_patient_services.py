from datetime import datetime

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from exceptions.exc import AppointmentNotFound
from model.patient_models import PatientCreate
from model.appointment_models import AppointmentOuter, AppointmentDateTime
from service.patient_services import (
    PatientService, PatientPage, PatientDataConstructor
)
from data.sql_models import Appointment, Patient
from tests.test_integration.conftest import BasePatientTest, appointment_status


@pytest.fixture
def patient_page(
        session: Session,
        patient_str_id: str,
        appointments: list[Appointment],
        link_services_to_appointments: None
) -> PatientPage:
    return PatientPage(session, patient_str_id)


@pytest.fixture
def appointment(
        appointments: list[Appointment], request: pytest.FixtureRequest
) -> Appointment:
    appointment = appointments[request.param]
    return appointment


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("appointments", "link_services_to_appointments")
class BasePatientPageTest(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _patient_page(self, patient_page: PatientPage) -> None:
        self.patient_page = patient_page


class TestPatientDataConstructor(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _service(self, session: Session, patient_str_id: str) -> None:
        self.service = PatientDataConstructor(session, patient_str_id)

    def test_exec(self) -> None:
        patient_data = self.service.exec()
        assert patient_data
        get_logger().debug(patient_data)


class TestPatientService(BasePatientTest):
    def test_check_input_data_returns_patient(
            self, patient_service: PatientService, patient: Patient
    ) -> None:  # TODO: test both workflows for new and existing patient
        create_data = PatientCreate(**patient.model_dump())
        patient_db = patient_service.check_input_data(create_data)
        assert patient_db is not None

    def test_check_input_data_reach_registry_clause__if_no_patient_exists(
            self,
            patient_service: PatientService,
            patient_create: PatientCreate
    ) -> None:
        patient_db = patient_service.check_input_data(patient_create)
        assert patient_db is not None
        patient_service.session.rollback()

    def test__check_existing_patient_returns_true(
            self, patient_service: PatientService, patient: Patient
    ) -> None:
        patient_exists = patient_service.check_patient_exists(patient.phone)
        assert patient_exists is not None

    def test__check_non_existing_patient_returns_false(
            self,
            patient_service: PatientService,
            patient_create: PatientCreate
    ) -> None:
        patient_exists = patient_service.check_patient_exists(
            patient_create.phone
        )
        assert patient_exists is None


class TestPatientPage(BasePatientPageTest):
    def test_init(self) -> None:
        assert self.patient_page.patient

    @pytest.mark.parametrize(
        "filtered_appointments", appointment_status, indirect=True
    )
    def test_get_appointments(
            self, filtered_appointments: list[AppointmentOuter]
    ) -> None:
        appointment_status, expected_result = filtered_appointments
        pending_appointments = self.patient_page.get_appointments(
            appointment_status
        )
        assert pending_appointments == expected_result

    def test_get_appointment_raises_appointment_not_found(self) -> None:
        with pytest.raises(AppointmentNotFound):
            self.patient_page.get_appointment(0)

    def test_update_info_succeed(
            self, session: Session, patient_update_info: PatientCreate
    ) -> None:
        self.patient_page.update_info(patient_update_info)
        updated_phone = patient_update_info.phone
        updated_patient_page = PatientPage(session, self.patient_page.patient.id)
        assert updated_patient_page.patient.phone == updated_phone


@pytest.mark.parametrize("appointment", [0], indirect=True)
class TestPatientPageSingleAppointment(BasePatientPageTest):
    def test_get_appointment_returns_target_result(
            self, appointment: Appointment
    ) -> None:
        appointment = self.patient_page.get_appointment(appointment.id)
        assert appointment

    def test_cancel_appointment_succeed(
            self, appointment: Appointment
    ) -> None:
        assert appointment.status == "pending"
        self.patient_page.change_appointment_status(appointment.id, "cancelled")
        assert appointment.status == "cancelled"
        appointment_db = self.patient_page.appointment_crud._get(appointment.id)
        get_logger().debug(appointment_db.status)

    def test_reschedule_appointment_succed(
            self,
            appointment: Appointment,
            reschedule_appointment_form: AppointmentDateTime
    ) -> None:
        appointment_date, appointment_time = appointment.date, appointment.time
        self.patient_page.reschedule_appointment(
            appointment.id, reschedule_appointment_form
        )
        assert not appointment_date == appointment.date
        assert not appointment_time == appointment.time
        assert appointment.date == reschedule_appointment_form.date
        assert appointment.time == reschedule_appointment_form.time

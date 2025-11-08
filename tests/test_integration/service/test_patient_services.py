import pytest
from sqlmodel import Session

from logger.setup import get_logger
from exceptions.exc import AppointmentNotFound
from model.patient_models import PatientCreate
from model.appointment_models import AppointmentOuter
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


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("appointments", "link_services_to_appointments")
class TestPatientPage(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _patient_page(self, patient_page: PatientPage) -> None:
        self.patient_page = patient_page

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

    def test_get_appointment_returns_target_result(
            self, appointments: list[Appointment]
    ) -> None:
        appointment = self.patient_page.get_appointment(appointments[0].id)
        assert appointment

    def test_get_appointment_raises_appointment_not_found(self) -> None:
        with pytest.raises(AppointmentNotFound):
            self.patient_page.get_appointment(0)

    def test_cancel_appointment_succeed(
            self, appointments: list[Appointment]
    ) -> None:
        appointment = appointments[0]
        assert appointment.status == "pending"
        self.patient_page.change_appointment_status(appointment.id, "cancelled")
        assert appointment.status == "cancelled"
        appointment_db = self.patient_page.appointment_crud._get(appointment.id)
        get_logger().debug(appointment_db.status)

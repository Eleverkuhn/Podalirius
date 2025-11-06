import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from model.appointment_models import AppointmentOuter
from service.patient_services import PatientService, PatientPage
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


class TestPatientService(BasePatientTest):
    def test_construct_patient_data(
            self,
            patient_service: PatientService,
            patient: Patient
    ) -> None:
        patient_id = patient_service.crud.uuid_to_str(patient.id)
        patient_data = patient_service.construct_patient_data(patient_id)
        assert patient_data

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

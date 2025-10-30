import pytest

from model.patient_models import PatientCreate
from service.patient_services import PatientService
from data.patient_data import Patient


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
class TestPatientService:
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

import pytest

from model.patient_models import PatientCreate
from data.patient_data import PatientCRUD, Patient


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
class TestPatientCRUD:
    def test_create_returns_patient_entry(
            self,
            patient_crud: PatientCRUD,
            patient_create: PatientCreate
    ) -> None:
        patient = patient_crud.create(patient_create)
        assert patient.id
        patient_crud.session.rollback()

    def test_get_by_phone(
            self, patient_crud: PatientCRUD, patient: Patient
    ) -> None:
        patient_db = patient_crud.get_by_phone(patient.phone)
        assert patient_db.phone == patient.phone

    def test_get(
            self, patient_crud: PatientCRUD, patient: Patient
    ) -> None:
        str_uuid = patient_crud.uuid_to_str(patient.id)
        patient_db = patient_crud.get(str_uuid)
        assert patient_db.phone == patient.phone
        assert patient_db.id == str_uuid

    def test_convert_to_patient_inner(
            self, patient_sql_model: Patient
    ) -> None:
        patient_inner = PatientCRUD.convert_to_patient_outer(patient_sql_model)
        assert type(patient_inner.id) is str

    def test_convert_birth_date_to_str(
            self,
            patient: Patient,
            patients_data: dict[str, str]
    ) -> None:
        dumped_patient = patient.model_dump()
        PatientCRUD.convert_birth_date_to_str(dumped_patient)
        converted_birth_date = dumped_patient.get("birth_date")
        assert converted_birth_date == patients_data.get("birth_date")

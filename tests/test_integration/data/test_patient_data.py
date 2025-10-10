import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from data.patient_data import PatientCRUD, PatientSQLModel


@pytest.fixture
def crud(session: Session) -> PatientCRUD:
    return PatientCRUD(session)


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
class TestPatientCRUD:
    def test_create_returns_patient_entry(
            self, crud: PatientCRUD, patient_create: PatientCreate) -> None:
        patient = crud.create(patient_create)
        assert patient.id
        crud.session.rollback()

    def test_convert_to_patient_inner(
            self, patient_sql_model: PatientSQLModel
    ) -> None:
        patient_inner = PatientCRUD.convert_to_patient_outer(patient_sql_model)
        assert type(patient_inner.id) is str

    def test_get_by_phone(
            self, crud: PatientCRUD, patient: PatientSQLModel
    ) -> None:
        patient_db = crud.get_by_phone(patient.phone)
        assert patient_db.phone == patient.phone

    def test_get(self, crud: PatientCRUD, patient: PatientSQLModel) -> None:
        str_uuid = crud.uuid_to_str(patient.id)
        patient_db = crud.get(str_uuid)
        assert patient_db.phone == patient.phone
        assert patient_db.id == str_uuid

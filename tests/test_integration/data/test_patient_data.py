import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from data.patient_data import PatientCRUD, PatientSQLModel


@pytest.fixture
def crud(session: Session) -> PatientCRUD:
    return PatientCRUD(session)


@pytest.mark.parametrize(
    "test_data", ["test_patients.json"], indirect=True
)
class TestPatientCRUD:
    @pytest.mark.parametrize(
        "build_test_data", [(PatientCreate, "patient_1")], indirect=True
    )
    def test_create_returns_patient_entry(
            self, crud: PatientCRUD, build_test_data: PatientCreate) -> None:
        patient = crud.create(build_test_data)
        assert patient.id
        assert patient.created_at
        assert patient.updated_at
        crud.session.rollback()

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test_convert_to_patient_inner(
            self, build_test_data: PatientSQLModel) -> None:
        patient_inner = PatientCRUD.convert_to_patient_outer(build_test_data)
        assert type(patient_inner.id) is str

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test_get_by_phone(
            self, crud: PatientCRUD, test_entry: PatientSQLModel) -> None:
        patient = crud.get_by_phone(test_entry.phone)
        assert patient.phone == test_entry.phone

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test_get(self, crud: PatientCRUD, test_entry: PatientSQLModel) -> None:
        str_uuid = crud.uuid_to_str(test_entry.id)
        patient = crud.get(str_uuid)
        assert patient.phone == test_entry.phone
        assert patient.id == str_uuid

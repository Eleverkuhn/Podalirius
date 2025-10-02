from datetime import date

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from data.patient_data import PatientCRUD, PatientSQLModel


test_data = [
    {
        "last_name": "TestLastname",
        "middle_name": "TestMiddlename",
        "first_name": "TestFirstname",
        "phone": "9999999999",
        "birth_date": date(2001, 1, 1)
    },
]


@pytest.fixture
def crud(session: Session) -> PatientCRUD:
    get_logger().debug("Inside `crud`")
    return PatientCRUD(session)


class TestPatientCRUD:
    @pytest.mark.parametrize(
        "build_test_data", [(PatientCreate, test_data[0])], indirect=True)
    def test_create_returns_patient_entry(
            self, crud: PatientCRUD, build_test_data: PatientCreate) -> None:
        patient = crud.create(build_test_data)
        assert patient.id
        assert patient.created_at
        assert patient.updated_at
        crud.session.rollback()

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, test_data[0])], indirect=True)
    def test_convert_to_patient_inner(
            self, build_test_data: PatientSQLModel) -> None:
        patient_inner = PatientCRUD.convert_to_patient_inner(build_test_data)
        assert type(patient_inner.id) is str

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, test_data[0])], indirect=True)
    def test_get_by_phone(
            self, crud: PatientCRUD, test_entry) -> None:
        patient = crud.get_by_phone(test_entry.phone)
        assert patient.phone == test_entry.phone

import random

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from exceptions import DataDoesNotMatch
from model.patient_models import PatientCreate, PatientOuter
from service.patient_services import PatientService
from data.patient_data import PatientSQLModel, PatientCRUD


@pytest.fixture
def patient_service(session: Session) -> PatientService:
    return PatientService(session)


@pytest.fixture
def registered_phone(create_test_patient: PatientSQLModel) -> str:
    return create_test_patient.phone


@pytest.fixture
def unregistered_phone() -> str:
    return str(random.randint(1000000000, 9999999999))


@pytest.fixture
def unmatching_patient_create_data(
        patient_create_data: PatientCreate,
        patient_update_data: dict[str, str]) -> PatientCreate:
    dumped = patient_create_data.model_dump()
    dumped.update(patient_update_data)
    updated_patient_create_data = PatientCreate(**dumped)
    return updated_patient_create_data


@pytest.mark.parametrize(
    "test_data", ["test_patients.json"], indirect=True
)
@pytest.mark.usefixtures("test_data")
class TestPatientService:
    def build__compare_data(
            self, patient: PatientSQLModel
    ) -> tuple[PatientOuter, PatientCreate]:
        patient_db = PatientCRUD.convert_to_patient_outer(patient)
        patient_input = PatientCreate(**patient.model_dump())
        return patient_db, patient_input

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test__compare_returns_ture_for_correct_input(
            self, build_test_data: PatientSQLModel
    ) -> None:
        data_matches = PatientService._compare(
            *self.build__compare_data(build_test_data)
        )
        assert data_matches is True

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test__compare_raises_error_if_input_does_not_match(
            self, build_test_data: PatientSQLModel
    ) -> None:
        patient_db, patient_input = self.build__compare_data(build_test_data)
        patient_input.first_name = "unmatchingfirstname"
        with pytest.raises(DataDoesNotMatch):
            PatientService._compare(patient_db, patient_input)

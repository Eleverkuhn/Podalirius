import random

import pytest
from sqlmodel import Session

from exceptions import DataDoesNotMatch
from model.patient_models import PatientCreate
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


class TestPatientService:
    def test_check_returns_patient_data_if_all_the_checks_are_passed(
            self,
            patient_service: PatientService,
            create_test_patient: PatientSQLModel,
            patient_create_data: PatientCreate) -> None:
        patient = patient_service.check_input_data(patient_create_data)
        assert patient is not None

    def test_check_input_data_registries_patient(
            self,
            session: Session,
            patient_service: PatientService,
            patient_create_data: PatientCreate) -> None:
        patient = patient_service.check_input_data(patient_create_data)
        crud = PatientCRUD(session)
        patient_from_db = crud.get(patient.id)
        assert patient_from_db is not None
        crud.delete_raw(crud.uuid_to_bytes(patient.id))  # FIX: refactor this

    def test__check_existing_patient_returns_true(
            self,
            patient_service: PatientService,
            registered_phone: str) -> None:
        patient_exists = patient_service._check_patient_exsits(
            registered_phone
        )
        assert patient_exists is not None

    def test__check_non_existing_patient_returns_false(
            self,
            patient_service: PatientService,
            unregistered_phone: str) -> None:
        patient_exists = patient_service._check_patient_exsits(
            unregistered_phone
        )
        assert patient_exists is None

    def test__compare_returns_ture_for_correct_input(
            self,
            patient_service: PatientService,
            patient_create_data: PatientCreate) -> None:
        data_matches = patient_service._compare(
            patient_create_data, patient_create_data
        )
        assert data_matches is True

    def test__compare_raises_error_if_input_does_not_match(
            self,
            patient_service: PatientService,
            patient_create_data: PatientCreate,
            unmatching_patient_create_data: PatientCreate) -> None:
        with pytest.raises(DataDoesNotMatch):
            patient_service._compare(
                patient_create_data, unmatching_patient_create_data
            )

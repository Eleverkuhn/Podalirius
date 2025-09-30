import uuid
import time
from datetime import date, datetime

import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound, IntegrityError

from data.patient_data import PatientSQLModel, PatientCRUD
from model.patient_models import PatientCreate


@pytest.fixture
def uuid_bytes() -> bytes:
    return uuid.uuid4().bytes


@pytest.fixture
def patient_sql_model(
        uuid_bytes: bytes,
        phone_number: str,
        birth_date_converted: date) -> PatientSQLModel:
    return PatientSQLModel(
        id=uuid_bytes,
        last_name="last",
        middle_name="middle",
        first_name="first",
        phone=phone_number,
        birth_date=birth_date_converted,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


class TestPatientCRUD:
    def test_uuid_to_str(self, uuid_bytes: bytes) -> None:
        str_uuid = PatientCRUD.uuid_to_str(uuid_bytes)
        assert str_uuid == str(uuid.UUID(bytes=uuid_bytes))

    def test_uuid_to_bytes(self, uuid_str: str) -> None:
        bytes_uuid = PatientCRUD.uuid_to_bytes(uuid_str)
        assert bytes_uuid == uuid.UUID(uuid_str).bytes

    def test_dump_patient_model(
            self, patient_sql_model: PatientSQLModel) -> None:
        dumped_patient = PatientCRUD.dump_patient_model(patient_sql_model)
        assert type(dumped_patient.id) is str

    def test_create_raw(
            self,
            session: Session,
            patient_create_data: PatientCreate,  # ) -> None:
            cleanup_created_entries: list[None | PatientSQLModel]) -> None:
        patient = PatientCRUD(session).create_raw(patient_create_data)
        cleanup_created_entries.append(patient)
        assert patient.phone == patient_create_data.phone

    def test_create_raw_raises_integrity_error_for_existing_patient(
            self,
            session: Session,
            patient_create_data: PatientCreate,
            create_test_patient: PatientSQLModel) -> None:
        with pytest.raises(IntegrityError):
            PatientCRUD(session).create_raw(patient_create_data)

    def test_get_raw(
            self,
            session: Session,
            create_test_patient: PatientSQLModel) -> None:
        patient = PatientCRUD(session).get_raw(create_test_patient.id)
        assert patient.phone == create_test_patient.phone

    def test_get_raw_raises_no_result_found_if_no_patient(
            self, session: Session, uuid_bytes: bytes) -> None:
        with pytest.raises(NoResultFound):
            PatientCRUD(session).get_raw(uuid_bytes)

    def test_update_raw(
            self,
            session: Session,
            create_test_patient: PatientSQLModel,
            patient_update_data: dict[str, str]) -> None:
        updated_patient = PatientCRUD(session).update_raw(
            create_test_patient.id, patient_update_data)
        get_updated_patient = PatientCRUD(session).get_raw(create_test_patient.id)
        assert updated_patient.last_name == get_updated_patient.last_name

    def test_delete_raw(
            self,
            session: Session,
            create_test_patient: PatientSQLModel) -> None:
        PatientCRUD(session).delete_raw(create_test_patient.id)
        statement = select(PatientSQLModel).where(
            PatientSQLModel.id == create_test_patient.id)
        with pytest.raises(NoResultFound):
            result = session.exec(statement)
            assert result.one()

    def test_create(
            self,
            session: Session,
            patient_create_data: PatientCreate) -> None:
        patient = PatientCRUD(session).create(patient_create_data)
        patient_id = uuid.UUID(patient.id).bytes
        statement = select(PatientSQLModel).where(
            PatientSQLModel.id == patient_id
        )
        db_patient = session.exec(statement).one()
        assert patient.phone == db_patient.phone
        session.delete(db_patient)
        session.commit()

    def test_get(
            self,
            session: Session,
            patient_create_data: PatientCreate,
            patient_uuid_str: str) -> None:
        patient = PatientCRUD(session).get(patient_uuid_str)
        assert patient == patient_create_data

    def test_update(
            self,
            session: Session,
            patient_uuid_str: str,
            patient_update_data: dict[str, str]) -> None:
        updated_patient = PatientCRUD(session).update(
            patient_uuid_str, patient_update_data)
        db_patient = PatientCRUD(session).get(patient_uuid_str)
        assert updated_patient == db_patient

    def test_update_changes_updated_at_time(
            self,
            session: Session,
            create_test_patient: PatientSQLModel,
            patient_uuid_str: str,
            patient_update_data: dict[str, str]) -> None:
        old_update_at = create_test_patient.updated_at
        time.sleep(1)
        PatientCRUD(session).update(
            patient_uuid_str, patient_update_data)
        db_patient_raw = PatientCRUD(session).get_raw(create_test_patient.id)
        assert old_update_at < db_patient_raw.updated_at

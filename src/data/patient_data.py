from typing import override
from uuid import UUID, uuid4
from datetime import date, datetime

from sqlmodel import Field, Session, select

from model.patient_models import PatientCreate, Patient
from data.crud import BaseCRUD
from data.base_sql_models import PersonSQLModel


class PatientSQLModel(PersonSQLModel, table=True):
    __tablename__ = "patients"

    id: bytes = Field(primary_key=True, default=uuid4().bytes)
    phone: str
    birth_date: date


class PatientCRUD(BaseCRUD):
    @override
    def __init__(
            self,
            session: Session,
            sql_model: PatientSQLModel = PatientSQLModel, # TODO: refactor this as in InitSeed in 'seed_db.py'
            return_model: Patient = Patient) -> None:
        super().__init__(session, sql_model, return_model)

    def create(self, patient_data: PatientCreate) -> Patient:
        patient = self.create_raw(patient_data)
        dumped_patient = self.dump_patient_model(patient)
        return dumped_patient

    def get(self, patient_id: str) -> PatientCreate:
        bytes_patient_id = self.__class__.uuid_to_bytes(patient_id)
        db_patient = self.get_raw(bytes_patient_id)
        dumped_patient = self.dump_patient_model_out(db_patient)
        return dumped_patient

    def _get_by_phone(self, phone: str) -> PatientCreate:
        """
        Temporal methhod. Needed for `AppointmentBooking`
        """
        with self.session as session:
            statement = select(self.sql_model).where(
                self.sql_model.phone == phone)
            result = session.exec(statement).one()
            return self.dump_patient_model(result)
            # return result.one()

    def update(self, patient_id: str, data: dict) -> PatientCreate:
        bytes_patient_id = self.__class__.uuid_to_bytes(patient_id)
        data["updated_at"] = datetime.now()
        updated_patient = self.update_raw(bytes_patient_id, data)
        dumped_patient = self.dump_patient_model_out(updated_patient)
        return dumped_patient

    @classmethod
    def uuid_to_str(cls, id: bytes) -> str:
        return str(UUID(bytes=id))

    @classmethod
    def uuid_to_bytes(cls, id: str) -> bytes:
        return UUID(id).bytes

    @classmethod
    def dump_patient_model(cls, created_patient: PatientSQLModel) -> Patient:
        patient = created_patient.model_dump()
        patient.update(
            {"id": cls.uuid_to_str(patient.get("id"))}
        )
        return Patient(**patient)

    def dump_patient_model_out(
            cls, patient_from_db: PatientSQLModel) -> PatientCreate:
        patient = patient_from_db.model_dump(exclude={
            "id", "created_at", "updated_at"
        })
        return PatientCreate(**patient)

    @override
    def create_raw(self, patient_data: PatientCreate) -> PatientSQLModel:
        return super().create_raw(patient_data)

    @override
    def get_raw(self, patient_id: bytes) -> PatientCreate:
        return super().get_raw(patient_id)

    @override
    def update_raw(self, patient_id: bytes, data: dict) -> PatientCreate:
        updated_patient = super().update_raw(patient_id, data)
        return updated_patient

    @override
    def delete_raw(self, id: int | bytes) -> None:
        super().delete_raw(id)

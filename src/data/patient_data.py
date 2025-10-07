from typing import override
from uuid import UUID, uuid4
from datetime import date

from sqlmodel import Field, Session

from model.patient_models import PatientInner, PatientOuter
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
            sql_model=PatientSQLModel,
            return_model=PatientInner) -> None:
        super().__init__(session, sql_model, return_model)
    
    def get(self, patient_id: str) -> PatientOuter:
        patient = super().get(self.uuid_to_bytes(patient_id))
        return self.convert_to_patient_outer(patient)

    def get_by_phone(self, phone: str) -> PatientOuter:
        patient = self._get_by_phone(phone)
        return self.convert_to_patient_outer(patient)

    def update(self, patient_id: str, data: dict) -> PatientOuter:
        patient = super().update(self.uuid_to_bytes(patient_id), data)
        return self.convert_to_patient_outer(patient)

    @classmethod
    def convert_to_patient_outer(
            cls, patient: PatientInner | PatientSQLModel) -> PatientOuter:
        dumped_patient = patient.model_dump()
        dumped_patient.update(
            {"id": cls.uuid_to_str(dumped_patient.get("id"))}
        )
        return PatientOuter(**dumped_patient)

    @classmethod
    def uuid_to_str(cls, id: bytes) -> str:
        return str(UUID(bytes=id))

    @classmethod
    def uuid_to_bytes(cls, id: str) -> bytes:
        return UUID(id).bytes

    def _get_by_phone(self, phone: str) -> PatientSQLModel:  # FIX:
        return self.session.exec(
            self.select.where(self.sql_model.phone == phone)
        ).one()

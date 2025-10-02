from typing import override
from uuid import UUID, uuid4
from datetime import date

from sqlmodel import Field, Session

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
            sql_model: type[PatientSQLModel] = PatientSQLModel) -> None:
        super().__init__(session, sql_model)

    def create(self, patient_data: PatientCreate) -> Patient:
        instance = self._convert_to_sql_model(patient_data.model_dump())
        patient = super()._create(instance)
        return self.convert_to_patient_inner(patient)

    def get(self, patient_id: str) -> Patient:
        patient = self._convert_id_and_get(patient_id)
        return self.convert_to_patient_inner(patient)

    def get_by_phone(self, phone: str) -> Patient:
        patient = self.session.exec(
            self.select.where(self.sql_model.phone == phone)
        ).one()
        return self.convert_to_patient_inner(patient)

    def update(self, patient_id: str, data: dict) -> Patient:
        patient = self._convert_id_and_get(patient_id)
        self._update(patient, data)
        return self.convert_to_patient_inner(patient)

    @classmethod
    def convert_to_patient_inner(
            cls, patient: PatientSQLModel) -> Patient:
        dumped_patient = patient.model_dump()
        dumped_patient.update(
            {"id": cls.uuid_to_str(dumped_patient.get("id"))}
        )
        return Patient(**dumped_patient)

    @classmethod
    def uuid_to_str(cls, id: bytes) -> str:
        return str(UUID(bytes=id))

    def _convert_id_and_get(self, patient_id: str) -> PatientSQLModel:  # TODO: find a better name
        bytes_patient_id = self.__class__.uuid_to_bytes(patient_id)
        return self._get(bytes_patient_id)

    @classmethod
    def uuid_to_bytes(cls, id: str) -> bytes:
        return UUID(id).bytes

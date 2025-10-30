from typing import override
from uuid import UUID

from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientInner, PatientOuter
from data.base_data import BaseCRUD
from data.sql_models import Patient


class PatientCRUD(BaseCRUD):
    @override
    def __init__(
            self,
            session: Session,
            sql_model=Patient,
            return_model=PatientInner
    ) -> None:
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
            cls, patient: PatientInner | Patient) -> PatientOuter:
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

    def _get_by_phone(self, phone: str) -> Patient:  # FIX:
        return self.session.exec(
            self.select.where(self.sql_model.phone == phone)
        ).one()

    @classmethod
    def convert_to_patient_inner(cls, patient: PatientOuter) -> PatientInner:
        dumped_patient = patient.model_dump()
        dumped_patient.update(
            {"id": cls.uuid_to_bytes(dumped_patient.get("id"))}
        )
        return PatientInner(**dumped_patient)

    @classmethod
    def convert_birth_date_to_str(cls, dumped_patient: dict) -> None:
        birth_date = dumped_patient.get("birth_date")
        get_logger().debug(type(birth_date))
        dumped_patient.update({"birth_date": birth_date.isoformat()})

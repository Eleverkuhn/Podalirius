from sqlmodel import Session

from model.specialty_models import SpecialtyOuter
from model.doctor_models import DoctorOuter
from data.base_data import BaseCRUD
from data.sql_models import Specialty
from data.doctor_data import DoctorDataConverter


class SpecialtyCRUD(BaseCRUD):
    def __init__(
            self,
            session: Session,
            sql_model: type[Specialty] = Specialty,
            return_model: type[SpecialtyOuter] = SpecialtyOuter
    ) -> None:
        super().__init__(session, sql_model, return_model)

    def get_by_title(self, title: str) -> SpecialtyOuter:
        specialty = self._get_by_title(title)
        specialty_outer = SpecialtyDataConverter(specialty).convert_to_outer()
        return specialty_outer

    def _get_by_title(self, title: str) -> Specialty:
        statement = self.select.where(self.sql_model.title == title)
        entry = self.session.exec(statement).one()
        return entry


class SpecialtyDataConverter:
    def __init__(self, specialty: Specialty) -> None:
        self.specialty = specialty

    @property
    def dumped(self) -> dict:
        dumped = self.specialty.model_dump()
        return dumped

    def convert_to_outer(self) -> SpecialtyOuter:
        doctors = self._get_doctors_outer()
        specialty_outer = SpecialtyOuter(**self.dumped, doctors=doctors)
        return specialty_outer

    def _get_doctors_outer(self) -> list[DoctorOuter]:
        doctor_data_converter = DoctorDataConverter(self.specialty.doctors)
        doctors_outer = doctor_data_converter.convert_multiple_doctors_to_outer()
        return doctors_outer

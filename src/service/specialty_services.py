from sqlmodel import Sequence

from service.base_services import BaseService
from service.doctor_services import DoctorDataConstructor
from data.crud import BaseCRUD
from data.sql_models import Doctor, Specialty


class SpecialtyDataConstructor(BaseService):
    def exec(self) -> list[Specialty]:
        specialties = BaseCRUD(self.session, Specialty, Specialty).get_all()
        traversed = self._traverse(specialties)
        return traversed

    def _traverse(self, specialties: Sequence[Specialty]) -> list[dict]:
        return [self._dump(specialty) for specialty in specialties]

    def _dump(self, specialty: Specialty) -> dict:
        dumped = specialty.model_dump(include=["id", "title"])
        dumped_with_doctors = self._add_doctors(dumped, specialty.doctors)
        return dumped_with_doctors

    def _add_doctors(
            self, dumped_specialty: dict[str, str], doctors: list[Doctor]
    ) -> dict:
        doctors = DoctorDataConstructor(self.session)._traverse(doctors)
        dumped_specialty.update({"doctors": doctors})
        return dumped_specialty

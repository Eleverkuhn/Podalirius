from typing import override

from fastapi import Depends
from sqlmodel import Session, Sequence

from service.base_services import BaseService
from service.doctor_services import DoctorDataConstructor
from data.connections import MySQLConnection
from data.base_data import BaseCRUD
from data.sql_models import Specialty


class SpecialtyPage(BaseService):
    @override
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.crud = BaseCRUD(session, Specialty, Specialty)

    def get_all_specialties(self) -> Sequence[Specialty]:
        specialties = self.crud.get_all()
        return specialties


class SpecialtyDataConstructor(BaseService):
    @override
    def __init__(
            self, session: Session, specialties: Sequence[Specialty]
    ) -> None:
        super().__init__(session)
        self.specialties = specialties

    @property
    def doctor_data_constructor(self) -> DoctorDataConstructor:
        constructor = DoctorDataConstructor(self.specialty.doctors)
        return constructor

    def exec(self) -> list[dict]:
        dumped_specialties = [
            self._dump(specialty) for specialty in self.specialties
        ]
        return dumped_specialties

    def _dump(self, specialty: Specialty) -> dict:
        self._set_specialty_data(specialty)
        self._add_doctors()
        return self.dumped_specialty

    def _set_specialty_data(self, specialty: Specialty) -> None:
        self.specialty = specialty
        self.dumped_specialty = specialty.model_dump(include=["id", "title"])

    def _add_doctors(self) -> None:
        doctors = self.doctor_data_constructor.exec()
        self.dumped_specialty.update({"doctors": doctors})


def get_specialty_page(
        session: Session = Depends(MySQLConnection.get_session)
) -> SpecialtyPage:
    specialty_page = SpecialtyPage(session)
    return specialty_page

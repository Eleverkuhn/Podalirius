"""
Services for loading data to HTML select forms. Placed into a distinct module
due to import errors
"""

from typing import override

from fastapi import Depends, Request
from sqlmodel import Session, Sequence

from service.base_services import BaseService
from service.auth_services import AuthService
from service.patient_services import PatientDataConstructor
from service.specialty_services import SpecialtyDataConstructor
from data.connections import MySQLConnection
from data.base_data import BaseCRUD
from data.sql_models import Appointment, Specialty


class AppointmentBookingFormDataConstructor(BaseService):
    @override
    def __init__(self, session: Session, request: Request) -> None:
        super().__init__(session)
        self.appointment_crud = BaseCRUD(session, Appointment, Appointment)
        self.specialty_crud = BaseCRUD(session, Specialty, Specialty)
        self.cookies: dict[str, str] = request.cookies
        self.auth_service = AuthService(session)

    def exec(self) -> dict:
        """Initial method"""
        content = self._construct_content()
        return content

    def _construct_content(self) -> dict:
        content = {
            "patient": self._get_patient_data(),
            "specialties": self._get_specialties_data()
        }
        return content

    def _get_patient_data(self) -> dict:
        patient_id = self.auth_service.authorize(self.cookies)
        patient_data = self._construct_patient_data(patient_id)
        return patient_data

    def _construct_patient_data(self, patient_id: str) -> dict:
        constructor = PatientDataConstructor(self.session, patient_id)
        patient_data = constructor.exec()
        return patient_data

    def _get_specialties_data(self) -> None:
        specialties = self.specialty_crud.get_all()
        specialties_data = self._construct_specialties_data(specialties)
        return specialties_data

    def _construct_specialties_data(
            self, specialties: Sequence[Specialty]
    ) -> list[dict]:
        constructor = SpecialtyDataConstructor(self.session, specialties)
        specialties_data = constructor.exec()
        return specialties_data


def get_booking_form_data_constructor(
        request: Request,
        session: Session = Depends(MySQLConnection.get_session),
) -> AppointmentBookingFormDataConstructor:
    constructor = AppointmentBookingFormDataConstructor(session, request)
    return constructor
    pass

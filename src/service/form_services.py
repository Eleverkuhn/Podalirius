"""
Services for loading data to HTML select forms. Placed into a distinct module
due to import errors
"""

from typing import override

from fastapi import Depends, Request
from sqlmodel import Session, Sequence

from exceptions.exc import UnauthorizedError
from service.base_services import BaseService
from service.auth_services import AuthService
from service.patient_services import PatientDataConstructor
from service.appointment_services import (
    AppointmentShceduleDataConstructor,
    AppointmentTimes
)
from service.specialty_services import SpecialtyDataConstructor
from service.doctor_services import DoctorDataConstructor
from data.connections import MySQLConnection
from data.base_data import BaseCRUD
from data.sql_models import Appointment, Specialty, Doctor


class AppointmentBookingFormDataConstructor(BaseService):
    @override
    def __init__(self, session: Session, request: Request) -> None:
        super().__init__(session)
        self.appointment_crud = BaseCRUD(session, Appointment, Appointment)
        self.specialty_crud = BaseCRUD(session, Specialty, Specialty)
        self.cookies: dict[str, str] = request.cookies
        self.auth_service = AuthService(session, request)

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
        try:
            patient_id = self.auth_service.authorize()
        except UnauthorizedError:
            patient_data = {}
        else:
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


class AppointmentRescheduleFormDataConstructor(BaseService):
    def __init__(self, session: Session, doctor_id: int) -> None:
        super().__init__(session)
        self.doctor_crud = BaseCRUD(session, Doctor, Doctor)
        self.doctor = self._get_doctor(int(doctor_id))
        self.doctor_data_constructor = DoctorDataConstructor(doctor=self.doctor)

    def _get_doctor(self, doctor_id: int) -> Doctor:
        doctor = self.doctor_crud._get(doctor_id)
        return doctor

    def exec(self) -> dict:
        appointment_schedule = self._get_appointment_schedule()
        return appointment_schedule

    def _get_appointment_schedule(self) -> dict:
        constructor = AppointmentShceduleDataConstructor(
            self._get_doctor_schedule(), self._get_doctor_appointments()
        )
        appointment_schedule = constructor.exec()
        return appointment_schedule

    def _get_doctor_schedule(self) -> dict:
        schedule = self.doctor_data_constructor._get_schedule()
        return schedule

    def _get_doctor_appointments(self) -> AppointmentTimes:
        appointments = self.doctor_data_constructor._get_appointments()
        return appointments


def get_booking_form_data_constructor(
        request: Request,
        session: Session = Depends(MySQLConnection.get_session),
) -> AppointmentBookingFormDataConstructor:
    constructor = AppointmentBookingFormDataConstructor(session, request)
    return constructor


def get_reschedule_data_constructor(
        id: int,
        session: Session = Depends(MySQLConnection.get_session)
) -> AppointmentRescheduleFormDataConstructor:
    constructor = AppointmentRescheduleFormDataConstructor(session, id)
    return constructor

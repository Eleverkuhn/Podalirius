from typing import override

from fastapi import Depends
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session

from exceptions.exc import DataDoesNotMatch, AppointmentNotFound
from model.patient_models import PatientCreate, PatientOuter
from model.appointment_models import AppointmentOuter, AppointmentDateTime
from service.base_services import BaseService
from service.auth_services import authorize
from data.connections import MySQLConnection
from data.base_data import BaseCRUD
from data.patient_data import PatientCRUD
from data.appointment_data import Appointment


class BasePatientService(BaseService):
    @override
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.crud = PatientCRUD(self.session)


class PatientDataConstructor(BasePatientService):
    @override
    def __init__(self, session: Session, patient_id: str) -> None:
        super().__init__(session)
        self.patient = self.crud.get(patient_id)

    def exec(self) -> dict[str, str]:
        dumped = self.patient.model_dump(exclude=["id"])
        self.crud.convert_birth_date_to_str(dumped)
        return dumped


class PatientService(BasePatientService):  # TODO: split this into Registry and ApponitmentCreationHelper
    def registry(self, create_data: PatientCreate) -> PatientOuter:
        """
        Separate method created for possible scalability
        """
        patient = self.crud.create(create_data)
        patient = self.crud.convert_to_patient_outer(patient)
        self.session.commit()
        return patient

    def construct_patient_data(self, patient_id: str) -> dict[str, str]:
        patient = self.crud.get(patient_id)
        dumped = patient.model_dump(exclude=["id"])
        self.crud.convert_birth_date_to_str(dumped)
        return dumped

    def check_input_data(
            self, patient_input_data: PatientCreate) -> PatientOuter:
        """
        The method is used in `AppointmentBooking`. Part of logic of
        creating an appointment for unlogged_in user
        """
        patient_db = self.check_patient_exists(patient_input_data.phone)
        if patient_db is not None:
            self._compare(patient_db, patient_input_data)
            patient_inner = self.crud.convert_to_patient_inner(patient_db)
            return patient_inner
        else:
            patient = self.crud.create(patient_input_data)
            return patient

    def check_patient_exists(self, phone: str) -> PatientOuter | None:
        try:
            patient = self.crud.get_by_phone(phone)
        except NoResultFound:
            return None
        else:
            return patient

    @classmethod
    def _compare(
            cls, patient_db: PatientOuter, patient_input: PatientCreate
    ) -> bool:
        if patient_input.is_submodel(patient_db):
            return True
        else:
            raise DataDoesNotMatch()


class PatientPage(BasePatientService):
    @override
    def __init__(self, session: Session, patient_id: str) -> None:
        super().__init__(session)
        self.patient = self.crud.get_with_appointments(patient_id)

    @property
    def patient_crud(self) -> PatientCRUD:
        patient_crud = PatientCRUD(self.session)
        return patient_crud

    @property
    def appointment_crud(self) -> BaseCRUD:
        appointment_crud = BaseCRUD(self.session, Appointment, Appointment)
        return appointment_crud

    @property
    def patient_public(self) -> PatientCreate:
        outer = PatientCreate(**self.patient.model_dump())
        return outer

    def update_info(self, form: PatientCreate) -> None:
        update_data = form.model_dump()
        self.patient_crud.update(self.patient.id, update_data)
        self.session.commit()

    def reschedule_appointment(
            self, id: int, form: AppointmentDateTime
    ) -> None:
        update_data = form.model_dump()
        self._update_appointment(id, update_data)

    def change_appointment_status(self, id: int, status: str) -> None:
        update_data = self._prepare_update_appointment_data(id, status)
        self._update_appointment(id, update_data)

    def _prepare_update_appointment_data(self, id: int, status: str) -> dict:
        appointment = self.get_appointment(id)
        appointment.status = status
        appointment_dumped = appointment.model_dump(exclude=["doctor", "price"])
        return appointment_dumped

    def _update_appointment(self, id: int, update_data: dict) -> None:
        self.appointment_crud.update(id, update_data)
        self.session.commit()

    def get_appointment(self, id: int) -> AppointmentOuter:
        for appointment in self.patient.appointments:
            if appointment.id == id:
                return appointment
        else:
            raise AppointmentNotFound()

    def get_appointments(self, status: str) -> list[AppointmentOuter]:
        filtered_appointments = [
                appointment
                for appointment
                in self.patient.appointments
                if appointment.status == status
            ]
        sorted_appointments = self._sort_appointments_by_date(
            filtered_appointments
        )
        return sorted_appointments

    def _sort_appointments_by_date(
            self, appointments: list[AppointmentOuter]
    ) -> list[AppointmentOuter]:
        sorted_appointments = sorted(
            appointments, key=lambda appointment: appointment.date
        )
        return sorted_appointments


def get_patient_page(
        session: Session = Depends(MySQLConnection.get_session),
        patient_id: str = Depends(authorize)
) -> PatientPage:
    patient_page = PatientPage(session, patient_id)
    return patient_page

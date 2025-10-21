from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from fastapi import Depends

from logger.setup import get_logger
from exceptions.exc import DataDoesNotMatch, FormInputError, UnauthorizedError
from model.form_models import AppointmentBookingForm
from model.appointment_models import (
    Appointment, AppointmentCreate, ServiceToAppointment
)
from model.patient_models import PatientCreate
from service.auth_services import AuthService, JWTTokenService
from service.patient_services import PatientService
from data import sql_models
from data.mysql import get_session
from data.crud import BaseCRUD
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientCRUD


class AppointmentBooking:
    def __init__(self, session: Session) -> None:
        self.session = session

    def book(
            self, cookies: dict[str, str], form: AppointmentBookingForm
    ) -> str:
        """
        Initial method which will start appointment booking process
        """
        patient_id = self._check_user_is_logged_in(cookies)
        if patient_id:
            return self._booking_for_logged_in_user()
        return self._booking_for_unlogged_in_user(form)

    def _check_user_is_logged_in(self, cookies: dict[str, str]) -> str | None:
        try:
            patient_id = AuthService(self.session).authorize(cookies)
        except UnauthorizedError:
            return None
        else:
            return patient_id

    def _booking_for_logged_in_user(self) -> None:
        pass

    def _booking_for_unlogged_in_user(
            self, form: AppointmentBookingForm
    ) -> str:
        try:
            patient = PatientService(self.session).check_input_data(
                form.get_patient_data()
            )
            appointment = self._create_appointment(patient.id, form)
        except DataDoesNotMatch:
            self.session.rollback()
            raise FormInputError((
                "You are trying to book an appointment for existing user with"
                "wrong data."
            ))
        except IntegrityError as exc:  # INFO: temp exception handler in case if something went wrong
            self.session.rollback()
            return exc
        else:
            self.session.commit()
            self._create_entry_in_services_to_appointments(
                appointment.id, form.service_id
            )
            token = JWTTokenService().create(appointment.id)
            return token

    def _create_appointment(
            self, patient_id: bytes, form: AppointmentBookingForm
    ) -> Appointment:
        appointment_data = self._construct_appointment_data(patient_id, form)
        appointment = AppointmentCrud(self.session).create(appointment_data)
        return appointment

    def _construct_appointment_data(
            self, patient_id: bytes, form: AppointmentBookingForm
    ) -> AppointmentCreate:
        return AppointmentCreate(**form.model_dump(), patient_id=patient_id)

    def _create_entry_in_services_to_appointments(
            self, appointment_id: int, service_id: int
    ) -> None:
        entry = ServiceToAppointment(
            appointment_id=appointment_id,
            service_id=service_id
        )
        BaseCRUD(
            self.session,
            sql_models.ServiceToAppointment,
            sql_models.ServiceToAppointment
        ).create(entry)
        self.session.commit()

    def render_form(self) -> None | PatientCreate:
        patient_id = self._check_user_is_logged_in()
        if patient_id:
            self.render_form_for_logged_in_user(patient_id)
        self.render_form_for_unlogged_in_user()

    def render_form_for_logged_in_user(self, patient_id: str) -> None:
        patient = PatientCRUD(self.session).get(patient_id)
        self.fill_appointment_form_with_user_info(patient)

    def fill_appointment_form_with_user_info(
            self, user: PatientCreate) -> None:
        # TODO: expand this with filling other fields
        pass

    def render_form_for_unlogged_in_user(self) -> None:
        # TODO: Maybe will be needed in the future. Remove otherwise
        pass


class AppointmentJWTTokenService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_appointment(self, token: str) -> Appointment:
        id = self._get_id_from_token(token)
        return AppointmentCrud(self.session).get(id)

    def _get_id_from_token(self, token: str) -> int:
        content = JWTTokenService().verify(token)
        return content.get("id")


def get_appointment_booking(
        session: Session = Depends(get_session),
) -> AppointmentBooking:
    return AppointmentBooking(session)


def get_appointment_jwt_token_service(
        session: Session = Depends(get_session),
) -> AppointmentJWTTokenService:
    return AppointmentJWTTokenService(session)

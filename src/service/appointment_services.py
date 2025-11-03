from datetime import date, time, datetime, timedelta
from typing import override

from sqlmodel import Session
from fastapi import Depends

from logger.setup import get_logger
from exceptions.exc import DataDoesNotMatch, FormInputError, UnauthorizedError
from model.form_models import AppointmentBookingForm
from model.patient_models import PatientOuter
from model.appointment_models import (
    AppointmentInner, AppointmentCreate
)
from service.base_services import BaseService
from service.auth_services import AuthService, JWTTokenService
from service.patient_services import PatientService
from service.specialty_services import SpecialtyDataConstructor
from data.connections import MySQLConnection
from data.base_data import BaseCRUD
from data.sql_models import Appointment, ServiceToAppointment

type AppointmentSchedule = dict[date, set[time]]


class BaseAppointmentService(BaseService):
    def _check_user_is_logged_in(self, cookies: dict[str, str]) -> str | None:
        try:
            patient_id = AuthService(self.session).authorize(cookies)
        except UnauthorizedError:
            return None
        else:
            return patient_id


class BaseAppointmentServiceWithCRUD(BaseService):
    @override
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.crud = BaseCRUD(session, Appointment, AppointmentInner)


class FormContent(BaseAppointmentService):
    """Service for rendering content of 'AppointmentBookingForm'"""
    def construct(self, cookies: dict[str, str]) -> dict:
        """Initial method"""
        patient = self._get_patient_from_cookies(cookies)
        specialties = SpecialtyDataConstructor(self.session).exec()
        content = {"patient": patient, "specialties": specialties}
        return content

    def _get_patient_from_cookies(self, cookies: dict[str, str]) -> dict | None:
        patient_id = self._check_user_is_logged_in(cookies)
        return self._get_patient_data(patient_id)

    def _get_patient_data(self, patient_id: str) -> dict | None:
        if patient_id:
            patient_data = PatientService(self.session).construct_patient_data(
                patient_id
            )
            return patient_data
        return None


class AppointmentShceduleDataConstructor:
    """Part of 'FormContent.construct()'"""
    def __init__(
            self,
            doctor_schedule: dict,
            appointment_times: list[datetime],
            booking_range: timedelta = timedelta(days=30)
    ) -> None:
        self.doctor_schedule = doctor_schedule
        self.booked_appointment_times = self._group_by_date(appointment_times)
        self._today = date.today()
        self.booking_range = self._set_booking_range(booking_range)
        self.schedule = {}

    @property
    def today(self) -> date:
        return self._today

    @today.setter
    def today(self, updated: date) -> None:
        self._today = updated

    @property
    def today_iso(self) -> str:
        return self.today.isoformat()

    @property
    def doctor_working_hours(self) -> set[str]:
        return self.doctor_schedule.get(self.today.weekday())

    def _group_by_date(
            self, appointment_times: list[datetime]
    ) -> AppointmentSchedule:
        schedule = {}
        for appointment_time in appointment_times:
            self._create_date_to_time_dict(schedule, appointment_time)
        return schedule

    def _create_date_to_time_dict(
            self, schedule: dict, appointment_time: datetime
    ) -> None:
        appointment_date = appointment_time.date()
        if schedule.get(appointment_date):
            schedule[appointment_date].add(appointment_time.time().isoformat())
        else:
            schedule[appointment_date] = {appointment_time.time().isoformat()}

    def _set_booking_range(self, booking_range: timedelta) -> date:
        return self.today + booking_range

    def exec(self) -> dict:
        while self.today < self.booking_range:
            self._check_doctor_working_hours()
            self._proceed_to_next_day()
        return self.schedule

    def _check_doctor_working_hours(self) -> None:
        if self.doctor_working_hours:
            self._set_free_appointment_dates()

    def _proceed_to_next_day(self) -> None:
        self.today += timedelta(days=1)

    def _set_free_appointment_dates(self) -> None:
        self._prepare_set_free_appointment_dates_data()
        self._set_free_appointment_times()

    def _prepare_set_free_appointment_dates_data(self) -> None:
        "Sets data for executing '_set_free_hours()'"
        self.booked_hours = self.booked_appointment_times.get(self.today)
        self._set_free_hours()

    def _set_free_hours(self) -> None:
        if self.booked_hours:
            self.free_hours = self.doctor_working_hours - self.booked_hours
            get_logger().debug(self.free_hours)
        else:
            self.free_hours = self.doctor_working_hours

    def _set_free_appointment_times(self) -> None:
        if self.free_hours:
            self.schedule[self.today_iso] = sorted(list(self.free_hours))


class AppointmentBooking(
        BaseAppointmentServiceWithCRUD, BaseAppointmentService
):
    def book(
            self, cookies: dict[str, str], form: AppointmentBookingForm
    ) -> str:
        """
        Initial method which starts appointment booking process
        """
        patient_id = self._check_user_is_logged_in(cookies)
        if patient_id:
            return self._booking_for_logged_in_user()
        return self._booking_for_unlogged_in_user(form)

    def _booking_for_logged_in_user(self) -> None:
        pass

    def _booking_for_unlogged_in_user(
            self, form: AppointmentBookingForm
    ) -> str:
        try:
            appointment = self._create_appointment(form)
        except DataDoesNotMatch:
            self._rollback()
        else:
            self._finish_transaction(appointment.id, form.service_id)
            token = JWTTokenService().create(appointment.id)
            return token

    def _create_appointment(
            self, form: AppointmentBookingForm
    ) -> Appointment:
        patient = self._get_patient_from_form(form)
        appointment = self._create_appointment_entry(patient.id, form)
        return appointment

    def _get_patient_from_form(
            self, form: AppointmentBookingForm
    ) -> PatientOuter:
        service = PatientService(self.session)
        patient = service.check_input_data(form.get_patient_data())
        return patient

    def _create_appointment_entry(
            self, patient_id: bytes, form: AppointmentBookingForm
    ) -> AppointmentInner:
        appointment_data = self._construct_appointment_data(patient_id, form)
        appointment = self.crud.create(appointment_data)
        return appointment

    def _construct_appointment_data(
            self, patient_id: bytes, form: AppointmentBookingForm
    ) -> AppointmentCreate:
        return AppointmentCreate(**form.model_dump(), patient_id=patient_id)

    def _finish_transaction(
            self, appointment_id: int, service_id: int
    ) -> None:
        self._create_services_to_appointments_entry(appointment_id, service_id)
        self.session.commit()

    def _create_services_to_appointments_entry(
            self, appointment_id: int, service_id: int
    ) -> None:
        entry = ServiceToAppointment(
            appointment_id=appointment_id,
            service_id=service_id
        )
        crud = BaseCRUD(
            self.session,
            ServiceToAppointment,
            ServiceToAppointment
        )
        crud.create(entry)

    def _rollback(self) -> None:
        self.session.rollback()
        raise FormInputError((
                "You are trying to book an appointment for existing user with"
                "wrong data."
            ))


class AppointmentJWTTokenService(BaseAppointmentServiceWithCRUD):
    def get_appointment(self, token: str) -> AppointmentInner:
        id = self._get_id_from_token(token)
        return self.crud.get(id)

    def _get_id_from_token(self, token: str) -> int:
        content = JWTTokenService().verify(token)
        return content.get("id")


def get_form_content(
        session: Session = Depends(MySQLConnection.get_session)
) -> FormContent:
    return FormContent(session)


def get_appointment_booking(
        session: Session = Depends(MySQLConnection.get_session),
) -> AppointmentBooking:
    return AppointmentBooking(session)


def get_appointment_jwt_token_service(
        session: Session = Depends(MySQLConnection.get_session),
) -> AppointmentJWTTokenService:
    return AppointmentJWTTokenService(session)

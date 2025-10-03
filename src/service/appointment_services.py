from sqlmodel import Session
from fastapi import Depends

from logger.setup import get_logger
from model.form_models import AppointmentBookingForm
from model.appointment_models import (
    Appointment, AppointmentCreate
)
from model.patient_models import PatientCreate
from service.patient_services import PatientService
from data.mysql import get_session
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientCRUD


class AppointmentBooking:
    def __init__(
            self,
            session: Session,
            form: AppointmentBookingForm,
            access_token: dict[str, str | None]) -> None:
        self.form = form
        self.session = session
        self.access_token = access_token

    @property
    def patient_id(self) -> str | None:
        return self.access_token.get("id")

    def book(self) -> None:
        """
        Initial method which will start appointment booking process
        """
        if self._check_user_is_logged_in():
            self._booking_for_logged_in_user()
        self._booking_for_unlogged_in_user()

    def _check_user_is_logged_in(self) -> str | bool:
        return self.patient_id is not None

    def _booking_for_logged_in_user(self) -> None:
        pass

    def _booking_for_unlogged_in_user(self) -> Appointment:
        try:
            patient = PatientService(self.session).check_input_data(
                self.form.get_patient_data()
            )
            appointment = self._create_appointment(patient.id)
            get_logger().debug(appointment)
        except Exception as exc:  # TODO: figure out exception type and manage exception handling
            self.session.rollback()  # TODO: to make this work I need to change
                                     #       my session handling logic
            return exc
        else:
            return appointment

    def _create_appointment(self, patient_id: bytes) -> Appointment:
        appointment_data = self._construct_appointment_data(patient_id)
        appointment = AppointmentCrud(self.session).create(
            appointment_data
        )
        return appointment

    def _construct_appointment_data(
            self, patient_id: bytes) -> AppointmentCreate:
        return AppointmentCreate(
            **self.form.get_appointment_data().model_dump(),
            patient_id=patient_id
        )
        
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


def get_appointment_booking(
        session: Session = Depends(get_session),
        form: AppointmentBookingForm = Depends(AppointmentBookingForm.empty),
        access_token: dict[str, str | None] = {}) -> AppointmentBooking:
    return AppointmentBooking(
        session, form, access_token)


def post_appointment_booking(
        session: Session = Depends(get_session),
        form: AppointmentBookingForm = Depends(AppointmentBookingForm.as_form),
        access_token: dict[str, str | None] = {}) -> AppointmentBooking:
    return AppointmentBooking(session, form, access_token)

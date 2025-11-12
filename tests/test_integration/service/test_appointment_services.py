from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from logger.setup import get_logger
from exceptions.exc import FormInputError
from model.form_models import AppointmentBookingForm
from model.appointment_models import AppointmentBase
from service.appointment_services import (
    AppointmentShceduleDataConstructor,
    AppointmentBooking,
    AppointmentJWTTokenService
)
from service.doctor_services import WorkScheduleDataConstructor
from data.sql_models import Appointment, Doctor
from data.patient_data import Patient
from utils import SetUpTest
from tests.test_integration.conftest import MockRequest, BasePatientTest


@pytest.fixture
def form(appointment_form_data: dict[str, str | int]) -> AppointmentBookingForm:
    return AppointmentBookingForm(**appointment_form_data)


@pytest.fixture
def booking_service(
        session: Session, mock_request: MockRequest
) -> AppointmentBooking:
    return AppointmentBooking(session, mock_request)


@pytest.fixture
def booking_service_unauthorized(
        session: Session, mock_request_with_no_cookies: MockRequest
) -> AppointmentBooking:
    return AppointmentBooking(session, mock_request_with_no_cookies)


@pytest.fixture
def appointment_model(
    appointment_form_data: dict[str, str | int]
) -> AppointmentBase:
    return AppointmentBase(**appointment_form_data)


class TestAppointmentScheduleDataConstructor:
    @pytest.mark.parametrize("doctor", [1], indirect=True)
    def test_doctor_with_fully_booked_day_returns_none(
            self, doctor: Doctor
    ) -> None:
        week_day = doctor.work_days[0]
        schedule_constructor = WorkScheduleDataConstructor(week_day)
        doctor_schedule = {int(week_day.weekday): schedule_constructor.exec()}
        booked = [
            (appointment.date, appointment.time)
            for appointment
            in doctor.appointments
            if appointment.date == date(2025, 11, 10)
        ]
        appointment_constructor = AppointmentShceduleDataConstructor(
            doctor_schedule, booked, timedelta(days=1)
        )
        appointment_constructor.today += timedelta(days=7)
        appoointment_schedule = appointment_constructor.exec()
        assert not appoointment_schedule


class TestAppointmentBookingForAuthorizedPatient(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _service(self, booking_service: AppointmentBooking) -> None:
        self.service = booking_service

    def test__booking_for_logged_in_user_is_succeed(
            self, cookies: dict[str, str]
    ) -> None:
        assert cookies
        get_logger().debug(cookies)

    def test__check_user_is_logged_in_returns_patient_id_if_logged_in(
            self, patient_str_id: str
    ) -> None:
        patient_id = self.service._check_user_is_logged_in()
        assert patient_id == patient_str_id


class TestAppointmentBookingForUnauthorizedPatient:
    @pytest.fixture(autouse=True)
    def _service(self, booking_service_unauthorized: AppointmentBooking) -> None:
        self.service = booking_service_unauthorized


    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointment_form_data", ["booking_form"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_existing_unlogged_in_user_succeed(
            self, form: AppointmentBookingForm,
    ) -> None:
        token = self.service._booking_for_unlogged_in_user(form)
        assert token

    @pytest.mark.parametrize(
        "appointment_form_data", ["booking_form"], indirect=True
    )
    def test__booking_for_unexistent_unlogged_in_user_succeed(
            self, form: AppointmentBookingForm, setup_test: SetUpTest,
    ) -> None:
        token = self.service._booking_for_unlogged_in_user(form)
        assert token
        setup_test.delete_patient(form.phone)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointment_form_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self, form: AppointmentBookingForm
    ) -> None:
        with pytest.raises(FormInputError):
            self.service._booking_for_unlogged_in_user(form)

    def test__check_user_is_logged_in_returns_none_if_unlogged_in(
            self,
    ) -> None:
        patient_id = self.service._check_user_is_logged_in()
        assert not patient_id


    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointment_form_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_entry_succeed(
            self,
            patient: Patient,
            appointment_model: AppointmentBase
    ) -> None:
        appointment = self.service._create_appointment_entry(
            patient.id, appointment_model
        )
        appointment_db = self.service.crud.get(appointment.id)
        result = appointment.model_dump(exclude=["created_at", "updated_at"])
        expected = appointment_db.model_dump(exclude=["created_at", "updated_at"])
        assert result == expected

    @pytest.mark.parametrize(
        "appointment_form_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_entry_fails_for_unexisting_patient(
            self,
            uuid_bytes: bytes,
            appointment_model: AppointmentBase
    ) -> None:
        with pytest.raises(IntegrityError):
            self.service._create_appointment_entry(
                uuid_bytes, appointment_model
            )


class TestAppointmentJWTTokenService:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["patient_1"], indirect=True
    )
    @pytest.mark.parametrize("get_appointment", [0], indirect=True)
    def test_get_appointment(
            self,
            appointment_token_service: AppointmentJWTTokenService,
            jwt_token_appointment: str,
            appointment: Appointment
    ) -> None:
        appointment_from_token = appointment_token_service.get_appointment(
            jwt_token_appointment
        )
        assert appointment_from_token.id == appointment.id

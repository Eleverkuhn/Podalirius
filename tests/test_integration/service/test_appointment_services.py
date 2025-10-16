import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from logger.setup import get_logger
from exceptions.exc import FormInputError
from model.form_models import AppointmentBookingForm
from service.appointment_services import (
    AppointmentBooking, AppointmentJWTTokenService
)
from data import sql_models
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientSQLModel
from utils import SetUpTest


@pytest.fixture
def appointment_booking_form(appointments_data: dict) -> AppointmentBookingForm:
    return AppointmentBookingForm(**appointments_data)


@pytest.fixture
def booking_service(
        session: Session,
        appointment_booking_form: AppointmentBookingForm
) -> AppointmentBooking:
    return AppointmentBooking(
        session,
        appointment_booking_form,
        {}
    )


class TestApointmentBooking:
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__booking_for_unlogged_in_user_succeed(
            self,
            booking_service: AppointmentBooking,
            setup_test: SetUpTest,
    ) -> None:
        token = booking_service._booking_for_unlogged_in_user()
        assert token
        get_logger().debug(token)
        setup_test.delete_patient(booking_service.form.phone)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.usefixtures("patients_data", "patient")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self, booking_service: AppointmentBooking,
    ) -> None:
        with pytest.raises(FormInputError):
            booking_service._booking_for_unlogged_in_user()
    
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patients_data")
    def test__create_appointment_succeed(
            self,
            session: Session,
            booking_service: AppointmentBooking,
            patient: PatientSQLModel
    ) -> None:
        appointment = booking_service._create_appointment(patient.id)
        appointment_from_db = AppointmentCrud(session).get(appointment.id)
        assert appointment.model_dump() == appointment_from_db.model_dump()
    
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_fails_for_unexisting_patient(
            self, booking_service: AppointmentBooking, uuid_bytes: bytes
    ) -> None:
        with pytest.raises(IntegrityError):
            booking_service._create_appointment(uuid_bytes)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_entry_in_services_to_appointments(
            self,
            booking_service: AppointmentBooking,
            appointment: sql_models.Appointment
    ) -> None:
        booking_service._create_entry_in_services_to_appoitments(
            appointment.id
        )
        statement = select(sql_models.ServiceToAppointment).where(
                sql_models.ServiceToAppointment.appointment_id == appointment.id
            )
        entry = booking_service.session.exec(statement).one()
        assert entry
        get_logger().debug(entry)


class TestAppointmentJWTTokenService:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_get_appointment(
            self,
            appointment_token_service: AppointmentJWTTokenService,
            jwt_token_appointment: str,
            appointment: sql_models.Appointment
    ) -> None:
        appointment_from_token = appointment_token_service.get_appointment(
            jwt_token_appointment
        )
        assert appointment_from_token.id == appointment.id

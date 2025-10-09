import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from logger.setup import get_logger
from exceptions import DataDoesNotMatch
from model.form_models import AppointmentBookingForm
from model.appointment_models import AppointmentCreate
from service.appointment_services import (
    AppointmentBooking, AppointmentJWTTokenService
)
from data import sql_models
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientCRUD, PatientSQLModel
from utils import SetUpTest


@pytest.fixture
def booking_service(
        session: Session,
        build_test_data: AppointmentBookingForm
) -> AppointmentBooking:
    return AppointmentBooking(
        session,
        build_test_data,
        {}
    )


@pytest.mark.parametrize(
    "test_data", ["test_appointments.json"], indirect=True
)
@pytest.mark.usefixtures("test_data")
class TestApointmentBooking:
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    def test__booking_for_unlogged_in_user_succeed(
            self,
            booking_service: AppointmentBooking,
            setup_test: SetUpTest,
    ) -> None:
        token = booking_service._booking_for_unlogged_in_user()
        assert token
        setup_test.delete_patient(booking_service.form.phone)

    @pytest.mark.parametrize(
        "test_entry",
        [(PatientSQLModel, "booking_form")],
        indirect=True
    )
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "miss_matched_user_data")],
        indirect=True
    )
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self,
            booking_service: AppointmentBooking,
            test_entry: PatientSQLModel
    ) -> None:
        with pytest.raises(DataDoesNotMatch):
            booking_service._booking_for_unlogged_in_user()

    @pytest.mark.parametrize(
        "test_entry",
        [(PatientSQLModel, "booking_form")],
        indirect=True
    )
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    def test__create_appointment_succeed(
            self,
            session: Session,
            booking_service: AppointmentBooking,
            test_entry: PatientSQLModel
    ) -> None:
        appointment = booking_service._create_appointment(
            test_entry.id
        )
        appointment_from_db = AppointmentCrud(session).get(appointment.id)
        assert appointment.model_dump() == appointment_from_db.model_dump()
    
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    def test__create_appointment_fails_for_unexisting_patient(
            self, booking_service: AppointmentBooking, uuid_bytes: bytes
    ) -> None:
        with pytest.raises(IntegrityError):
            booking_service._create_appointment(uuid_bytes)

    @pytest.mark.parametrize(
        "test_entry",
        [(PatientSQLModel, "booking_form")],
        indirect=True
    )
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    def test__create_entry_in_services_to_appointments(
            self,
            session: Session,
            build_test_data: AppointmentBookingForm,
            booking_service: AppointmentBooking,
            test_entry: PatientSQLModel
    ) -> None:
        appointment = AppointmentCrud(session).create(AppointmentCreate(
            **build_test_data.model_dump(), patient_id=test_entry.id
        ))
        booking_service._create_entry_in_services_to_appoitments(
            appointment.id
        )
        entry = session.exec(
            select(sql_models.ServiceToAppointment).where(
                sql_models.ServiceToAppointment.appointment_id == appointment.id
            )
        ).one()
        assert entry


class TestAppointmentJWTTokenService:
    @pytest.mark.parametrize("patient", ["patient_1"], indirect=True)
    @pytest.mark.parametrize("appointment", ["booking_form"], indirect=True)
    @pytest.mark.parametrize("jwt_token_appointment", [None], indirect=True)
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

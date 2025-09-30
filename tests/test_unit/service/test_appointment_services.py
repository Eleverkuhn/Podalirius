from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from model.form_models import AppointmentBookingForm
from model.appointment_models import AppointmentCreate
from model.patient_models import PatientCreate
from service.appointment_services import (
    AppointmentBooking,
    get_appointment_booking,
    post_appointment_booking
)
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientSQLModel, PatientCRUD


@pytest.fixture
def logged_in_user(
        session: Session, patient_uuid_str: str) -> AppointmentBooking:
    return get_appointment_booking(
        session=session, access_token={"id": patient_uuid_str})


@pytest.fixture
def unlogged_in_user(session: Session) -> AppointmentBooking:
    return post_appointment_booking(session=session)


@pytest.fixture
def appointment_no_patient_data(today: datetime) -> dict[str, datetime | int]:
    return {
        "date": today,
        "doctor_id": 1,
        "specialty_id": 1,
        "service_id": 1,
    }


@pytest.fixture
def appointment_booking_form_model(
        patient_create_data: PatientCreate,
        appointment_no_patient_data: dict[str, datetime | int]) -> AppointmentBookingForm:
    return AppointmentBookingForm(
        **patient_create_data.model_dump(),
        **appointment_no_patient_data
    )


@pytest.fixture
def appointment_booking_form_missmatched_patient(
        unmatching_patient_create_data: PatientCreate,
        appointment_no_patient_data: dict[str, datetime | int]
) -> AppointmentBookingForm:
    return AppointmentBookingForm(
        **unmatching_patient_create_data.model_dump(),
        **appointment_no_patient_data
    )


@pytest.fixture
def appointment_booking_with_data(
        session: Session,
        appointment_booking_form_model: AppointmentBookingForm
) -> AppointmentBooking:
    """
    Appointment booking service with predefined form data (not derived from
                                                           html form)
    """
    return AppointmentBooking(
        session,
        appointment_booking_form_model,
        {}
    )


@pytest.fixture
def appointment_booking_unmatching_data(
        session: Session,
        appointment_booking_form_missmatched_patient: AppointmentBookingForm
) -> AppointmentBooking:
    return AppointmentBooking(
        session,
        appointment_booking_form_missmatched_patient,
        {}
    )


@pytest.fixture
def appointment_create_data(
        create_test_patient: PatientSQLModel,
        appointment_no_patient_data: dict[str, datetime | int]
) -> AppointmentCreate:
    return AppointmentCreate(
        doctor_id=appointment_no_patient_data.get("doctor_id"),
        date=appointment_no_patient_data.get("date"),
        patient_id=create_test_patient.id
    )


class TestAppointmentBooking:
    def test__check_user_is_logged_in_returns_true_if_access_code(
            self, logged_in_user: AppointmentBooking) -> None:
        assert logged_in_user._check_user_is_logged_in() is True

    def test__check_user_is_logged_in_returns_false_if_no_access_code(
            self, unlogged_in_user: AppointmentBooking) -> None:
        assert unlogged_in_user._check_user_is_logged_in() is False

    def test__booking_for_unlogged_in_user_succeed(
            self,
            session: Session,
            cleanup_created_entries,
            appointment_booking_with_data: AppointmentBooking) -> None:
        appointment = appointment_booking_with_data._booking_for_unlogged_in_user()
        assert appointment
        patient = PatientCRUD(session).get_raw(appointment.patient_id)
        cleanup_created_entries.append(patient)

    @pytest.mark.skip(reason="Rollback doesn't work")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self,
            appointment_booking_unmatching_data: AppointmentBooking) -> None:
        appointment = appointment_booking_unmatching_data._booking_for_unlogged_in_user()
        assert appointment

    def test__create_appointment_succeed(
            self,
            session: Session,
            create_test_patient: PatientSQLModel,
            appointment_booking_with_data: AppointmentBooking) -> None:
        appointment = appointment_booking_with_data._create_appointment(
            create_test_patient.id
        )
        appointment_from_db = AppointmentCrud(session).get_raw(appointment.id)
        assert appointment.is_submodel(appointment_from_db)

    def test__create_appointment_fails_for_unexisting_patient(
            self,
            uuid_bytes: bytes,
            appointment_booking_with_data: AppointmentBooking) -> None:
        with pytest.raises(IntegrityError):
            appointment_booking_with_data._create_appointment(uuid_bytes)

    def test__construct_appointment_data(
            self,
            appointment_booking_with_data: AppointmentBooking,
            uuid_bytes: bytes) -> None:
        data = appointment_booking_with_data._construct_appointment_data(
            uuid_bytes
        )
        assert data is not None

    @pytest.mark.skip(reason="redundant")
    def test_render_form_is_none_for_unlogged_in_user(  # TODO: better naming
            self, unlogged_in_user: AppointmentBooking) -> None:
        assert unlogged_in_user.render_form() is None

    @pytest.mark.skip(reason="redundant")
    def test_redner_form_returns_user_if_logged_in(
            self,
            patient_create_data: PatientCreate,
            logged_in_user: AppointmentBooking) -> None:
        user = logged_in_user.render_form()
        assert user == patient_create_data

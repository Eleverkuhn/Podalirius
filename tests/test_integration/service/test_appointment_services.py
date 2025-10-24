from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from logger.setup import get_logger
from exceptions.exc import FormInputError
from model.form_models import AppointmentBookingForm
from model.appointment_models import AppointmentBase
from service.appointment_services import (
    BaseAppointmentService,
    FormContent,
    AppointmentBooking,
    AppointmentJWTTokenService
)
from data import sql_models
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientSQLModel
from utils import SetUpTest


@pytest.fixture
def form(appointments_data: dict[str, str | int]) -> AppointmentBookingForm:
    return AppointmentBookingForm(**appointments_data)


@pytest.fixture
def base_appointment_service(session: Session) -> BaseAppointmentService:
    return BaseAppointmentService(session)


@pytest.fixture
def form_content(session: Session) -> FormContent:
    return FormContent(session)


@pytest.fixture
def booking_service(session: Session) -> AppointmentBooking:
    return AppointmentBooking(session)


@pytest.fixture
def appointment_model(
    appointments_data: dict[str, str | int]
) -> AppointmentBase:
    return AppointmentBase(**appointments_data)


class TestBaseAppointmentService:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test__check_user_is_logged_in_returns_patient_id_if_logged_in(
            self,
            base_appointment_service: BaseAppointmentService,
            cookies: dict[str, str],
            patient_str_id: str
    ) -> None:
        patient_id = base_appointment_service._check_user_is_logged_in(cookies)
        assert patient_id == patient_str_id

    def test__check_user_is_logged_in_returns_none_if_unlogged_in(
            self, base_appointment_service: BaseAppointmentService
    ) -> None:
        cookies = {}
        patient_id = base_appointment_service._check_user_is_logged_in(cookies)
        assert not patient_id


class TestFormContent:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test_construct(
            self, form_content: FormContent, cookies: dict[str, str]
    ) -> None:
        assert form_content.construct(cookies)


class TestAppointmentBooking:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_existing_unlogged_in_user_succeed(
            self,
            booking_service: AppointmentBooking,
            form: AppointmentBookingForm,
            setup_test: SetUpTest,
    ) -> None:
        token = booking_service._booking_for_unlogged_in_user(form)
        assert token
        setup_test.delete_patient(form.phone)

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__booking_for_unexistent_unlogged_in_user_succeed(
            self,
            booking_service: AppointmentBooking,
            form: AppointmentBookingForm,
            setup_test: SetUpTest,
    ) -> None:
        token = booking_service._booking_for_unlogged_in_user(form)
        assert token
        setup_test.delete_patient(form.phone)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self,
            booking_service: AppointmentBooking,
            form: AppointmentBookingForm
    ) -> None:
        with pytest.raises(FormInputError):
            booking_service._booking_for_unlogged_in_user(form)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_succeed(
            self,
            booking_service: AppointmentBooking,
            patient: PatientSQLModel,
            appointment_model: AppointmentBase
    ) -> None:
        appointment = booking_service._create_appointment(
            patient.id, appointment_model
        )
        appointment_db = AppointmentCrud(booking_service.session).get(
            appointment.id
        )
        assert appointment.model_dump() == appointment_db.model_dump()

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_fails_for_unexisting_patient(
            self,
            booking_service: AppointmentBooking,
            uuid_bytes: bytes,
            appointment_model: AppointmentBase
    ) -> None:
        with pytest.raises(IntegrityError):
            booking_service._create_appointment(uuid_bytes, appointment_model)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_entry_in_services_to_appointments(
            self,
            booking_service: AppointmentBooking,
            appointment: sql_models.Appointment,
            appointments_data: dict[str, str | int]
    ) -> None:
        booking_service._create_entry_in_services_to_appointments(
            appointment.id, appointments_data.get("service_id")
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

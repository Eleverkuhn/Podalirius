import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from logger.setup import get_logger
from exceptions.exc import FormInputError
from model.form_models import AppointmentBookingForm
from model.auth_models import OTPCode
from model.appointment_models import AppointmentBase
from service.auth_services import JWTTokenService
from service.appointment_services import (
    AppointmentBooking, AppointmentJWTTokenService
)
from data import sql_models
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientSQLModel, PatientCRUD
from utils import SetUpTest


@pytest.fixture
def form(appointments_data: dict[str, str | int]) -> AppointmentBookingForm:
    return AppointmentBookingForm(**appointments_data)


@pytest.fixture
def service(session: Session) -> AppointmentBooking:
    return AppointmentBooking(session)


@pytest.fixture
def appointment_model(
    appointments_data: dict[str, str | int]
) -> AppointmentBase:
    return AppointmentBase(**appointments_data)


@pytest.fixture
def patient_str_id(patient: PatientSQLModel) -> str:
    return PatientCRUD.uuid_to_str(patient.id)


@pytest.fixture
def access_token(
        patient_str_id: str, jwt_token_service: JWTTokenService
) -> str:
    return jwt_token_service.create(patient_str_id)


@pytest.fixture
def cookies(access_token: str) -> dict[str, str]:
    return {"access_token": access_token}


class TestAppointmentBooking:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test__check_user_is_logged_in_returns_patient_id_if_logged_in(
            self,
            service: AppointmentBooking,
            cookies: dict[str, str],
            patient_str_id: str
    ) -> None:
        patient_id = service._check_user_is_logged_in(cookies)
        assert patient_id == patient_str_id

    def test__check_user_is_logged_in_returns_none_if_unlogged_in(
            self, service: AppointmentBooking
    ) -> None:
        cookies = {}
        patient_id = service._check_user_is_logged_in(cookies)
        assert not patient_id

    # @pytest.mark.skip(reason="...")
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_existing_unlogged_in_user_succeed(
            self,
            service: AppointmentBooking,
            form: AppointmentBookingForm,
            setup_test: SetUpTest,
    ) -> None:
        token = service._booking_for_unlogged_in_user(form)
        assert token
        setup_test.delete_patient(form.phone)

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__booking_for_unexistent_unlogged_in_user_succeed(
            self,
            service: AppointmentBooking,
            form: AppointmentBookingForm,
            setup_test: SetUpTest,
    ) -> None:
        token = service._booking_for_unlogged_in_user(form)
        assert token
        setup_test.delete_patient(form.phone)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.usefixtures("patient")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self, service: AppointmentBooking, form: AppointmentBookingForm
    ) -> None:
        with pytest.raises(FormInputError):
            service._booking_for_unlogged_in_user(form)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_succeed(
            self,
            service: AppointmentBooking,
            patient: PatientSQLModel,
            appointment_model: AppointmentBase
    ) -> None:
        appointment = service._create_appointment(patient.id, appointment_model)
        appointment_db = AppointmentCrud(service.session).get(appointment.id)
        assert appointment.model_dump() == appointment_db.model_dump()

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_appointment_fails_for_unexisting_patient(
            self,
            service: AppointmentBooking,
            uuid_bytes: bytes,
            appointment_model: AppointmentBase
    ) -> None:
        with pytest.raises(IntegrityError):
            service._create_appointment(uuid_bytes, appointment_model)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test__create_entry_in_services_to_appointments(
            self,
            service: AppointmentBooking,
            appointment: sql_models.Appointment,
            appointments_data: dict[str, str | int]
    ) -> None:
        service._create_entry_in_services_to_appointments(
            appointment.id, appointments_data.get("service_id")
        )
        statement = select(sql_models.ServiceToAppointment).where(
                sql_models.ServiceToAppointment.appointment_id == appointment.id
            )
        entry = service.session.exec(statement).one()
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

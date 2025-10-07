import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from exceptions import DataDoesNotMatch
from model.form_models import AppointmentBookingForm
from model.appointment_models import AppointmentCreate
from service.appointment_services import AppointmentBooking
from data import sql_models
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientCRUD, PatientSQLModel
from utils import SetUpTest


@pytest.fixture
def service(
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
            session: Session,
            service: AppointmentBooking,
            setup_test: SetUpTest,
    ) -> None:
        appointment = service._booking_for_unlogged_in_user()
        assert appointment
        setup_test._delete_entry(PatientCRUD(session)._get(
            appointment.patient_id
        ))

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
            self, service: AppointmentBooking, test_entry: PatientSQLModel
    ) -> None:
        with pytest.raises(DataDoesNotMatch):
            service._booking_for_unlogged_in_user()

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
            service: AppointmentBooking,
            test_entry: PatientSQLModel
    ) -> None:
        appointment = service._create_appointment(
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
            self, service: AppointmentBooking, uuid_bytes: bytes
    ) -> None:
        with pytest.raises(IntegrityError):
            service._create_appointment(uuid_bytes)

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
            service: AppointmentBooking,
            test_entry: PatientSQLModel
    ) -> None:
        appointment = AppointmentCrud(session).create(AppointmentCreate(
            **build_test_data.model_dump(), patient_id=test_entry.id
        ))
        service._create_entry_in_services_to_appoitments(
            appointment.id
        )
        entry = session.exec(
            select(sql_models.ServiceToAppointment).where(
                sql_models.ServiceToAppointment.appointment_id == appointment.id
            )
        ).one()
        assert entry

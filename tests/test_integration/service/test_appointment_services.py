import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from model.form_models import AppointmentBookingForm
from service.appointment_services import AppointmentBooking
from data.appointment_data import AppointmentCrud
from data.patient_data import PatientCRUD, PatientSQLModel


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
            setup
    ) -> None:
        appointment = service._booking_for_unlogged_in_user()
        assert appointment
        setup._delete_entry(PatientCRUD(session)._get(
            appointment.patient_id
        ))

    @pytest.mark.skip(reason="Rollback doesn't work")
    def test__booking_for_unlogged_in_user_rollbacks_if_miss_matched(
            self, service: AppointmentBooking
    ) -> None:
        appointment = service._booking_for_unlogged_in_user()
        assert appointment

    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    @pytest.mark.parametrize(
        "test_entry",
        [(PatientSQLModel, "booking_form")],
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

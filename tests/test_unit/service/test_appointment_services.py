import pytest

from model.form_models import AppointmentBookingForm
from service.appointment_services import AppointmentBooking


class TestAppointmentBooking:
    def test__check_user_is_logged_in_returns_true_if_access_code(
            self, uuid_str: str
    ) -> None:
        service = AppointmentBooking(None, None, {"id": uuid_str})
        assert service._check_user_is_logged_in() is True

    def test__check_user_is_logged_in_returns_false_if_no_access_code(
            self
    ) -> None:
        service = AppointmentBooking(None, None, {})
        assert service._check_user_is_logged_in() is False
        
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    @pytest.mark.usefixtures("appointments_data")
    def test__construct_appointment_data(
            self,
            appointment_booking_form: AppointmentBookingForm,
            uuid_bytes: bytes
    ) -> None:
        service = AppointmentBooking(None, appointment_booking_form, None)
        data = service._construct_appointment_data(uuid_bytes)
        assert data is not None

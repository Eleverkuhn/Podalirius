import uuid

import pytest

from model.form_models import AppointmentBookingForm
from service.appointment_services import AppointmentBooking


@pytest.fixture
def uuid_str() -> str:
    return str(uuid.uuid4())


@pytest.mark.parametrize(
    "test_data", ["test_appointments.json"], indirect=True
)
@pytest.mark.usefixtures("test_data")
class TestAppointmentBooking:
    def test__check_user_is_logged_in_returns_true_if_access_code(
            self, uuid_str: str
    ) -> None:
        service = AppointmentBooking(None, None, {"id": uuid_str})
        assert service._check_user_is_logged_in() is True

    def test__check_user_is_logged_in_returns_false_if_no_access_code(
            self) -> None:
        service = AppointmentBooking(None, None, {})
        assert service._check_user_is_logged_in() is False
        
    @pytest.mark.parametrize(
        "build_test_data",
        [(AppointmentBookingForm, "booking_form")],
        indirect=True
    )
    def test__construct_appointment_data(
            self,
            build_test_data: AppointmentBookingForm,
            uuid_bytes: bytes) -> None:
        service = AppointmentBooking(None, build_test_data, None)
        data = service._construct_appointment_data(uuid_bytes)
        assert data is not None

from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi import status
from pydantic import ValidationError

from model.form_models import AppointmentBookingForm
from tests.test_integration.web.conftest import BaseEndpointTest

type FormData = dict[str, str | int]


@pytest.fixture
def appointment_booking_form_data() -> FormData:
    return {
        "last_name": "last",
        "middle_name": "middle",
        "first_name": "first",
        "birth_date": "2025-09-05",
        "phone": "9999999999",
        "service_id": 1,
        "specialty_id": 1,
        "doctor_id": 1,
        "date": "2025-09-05T14:30:00"
    }


@pytest.fixture
def appointment_booking_form_data_with_missing_field(
        appointment_booking_form_data: FormData) -> FormData:
    appointment_booking_form_data.pop("date")
    return appointment_booking_form_data


@pytest.fixture
def appointment_booking_form_data_with_invalid_field(
        appointment_booking_form_data: FormData) -> FormData:
    appointment_booking_form_data.update({"last_name": "1232"})
    return appointment_booking_form_data


@pytest.fixture
def appointment_booking_form_data_with_multiple_invalid_fields(
        appointment_booking_form_data_with_invalid_field: FormData) -> FormData:
    appointment_booking_form_data_with_invalid_field.update(
        {
            "phone": "0",
            "middle_name": "23232"
        }
    )
    return appointment_booking_form_data_with_invalid_field


class TestAppointmentEndpoint(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "get_form": self.client.app.url_path_for(
                "Appointment.get_appointment_form"),
            "send_form": self.client.app.url_path_for(
                "Appointment.create_appointment")
        }

    def test_get_returns_blank_form_for_unlogged_in_user(self) -> None:
        response = self.get_request("get_form")
        soup = BeautifulSoup(response.text, "html.parser")
        form_fields = soup.find_all("input")
        for field in form_fields:
            assert field.get("value") == ""

    def test_appointment_form_redirects_to_main(
            self, appointment_booking_form_data: FormData) -> None:
        response = self.post_request(
            "send_form", appointment_booking_form_data
        )
        location = response.headers.get("location")
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert location == self.client.app.url_path_for("main")

    def test_missing_form_field_raises_unprocessable_entity(
            self,
            appointment_booking_form_data_with_missing_field: FormData
    ) -> None:
        response = self.post_request(
            "send_form", appointment_booking_form_data_with_missing_field
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_pydantyic_field_raises_validation_error(
            self,
            appointment_booking_form_data_with_invalid_field: FormData
    ) -> None:
        response = self.post_request(
            "send_form", appointment_booking_form_data_with_invalid_field
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_pydantic_field_error_msg_rendered_at_correct_form_field(
            self,
            appointment_booking_form_data_with_multiple_invalid_fields: FormData
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            AppointmentBookingForm(
                **appointment_booking_form_data_with_multiple_invalid_fields
            )
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = self.post_request(
            "send_form",
            appointment_booking_form_data_with_multiple_invalid_fields
        )
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [tag.get_text(strip=True) for tag in soup.find_all("small")]
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)

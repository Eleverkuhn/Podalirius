from datetime import timedelta
from time import sleep

import pytest
from bs4 import BeautifulSoup
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from logger.setup import get_logger
from exceptions.exc import DataDoesNotMatch
from utils import SetUpTest
from model.form_models import AppointmentBookingForm
from model.appointment_models import Appointment


@pytest.fixture
def url_appointment_created(
        client: TestClient, jwt_token_appointment: str
) -> str:
    base = client.app.url_path_for("Appointment.info")
    return "".join([base, f"?token={jwt_token_appointment}"])


class TestAppointmentEndpointGetForm:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Appointment.get_form"))
        assert response.status_code == status.HTTP_200_OK

    def test_get_returns_blank_form_for_unlogged_in_user(
            self, client: TestClient
    ) -> None:
        response = client.get(client.app.url_path_for("Appointment.get_form"))
        soup = BeautifulSoup(response.text, "html.parser")
        form_fields = soup.find_all("input")
        for field in form_fields:
            assert field.get("value") == ""


class TestAppointmentEndpointSendForm:
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_create_appointment_redirects_to_appointment_info_on_success(
            self,
            client: TestClient,
            appointments_data: dict,
            setup_test: SetUpTest,
    ) -> None:
        response = client.post(
            client.app.url_path_for("Appointment.send_form"),
            data=appointments_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        setup_test.delete_patient(appointments_data.get("phone"))

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_missing_form_field_returns_unprocessable_entity(
            self, client: TestClient, appointments_data: dict
    ) -> None:
        appointments_data.pop("date")
        response = client.post(
            client.app.url_path_for("Appointment.send_form"),
            data=appointments_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_invalid_pydantyic_field_raises_validation_error(
            self, client: TestClient, appointments_data: dict
    ) -> None:
        appointments_data.update({"last_name": "1232"})
        response = client.post(
            client.app.url_path_for("Appointment.send_form"),
            data=appointments_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "appointments_data", ["invalid_booking_form"], indirect=True
    )
    def test_invalid_pydantic_field_error_msg_rendered_at_correct_form_field(
            self, client: TestClient, appointments_data: dict
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            AppointmentBookingForm(**appointments_data)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = client.post(
            client.app.url_path_for("Appointment.send_form"),
            data=appointments_data
        )
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [
            tag.get_text(strip=True)
            for tag
            in soup.find_all("small")
        ]
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)

    @pytest.mark.parametrize(
        "appointments_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patient")
    def test_miss_matching_data_raises_request_validation_error(
            self,
            client: TestClient,
            appointments_data: dict,
            setup_test: SetUpTest,
    ) -> None:
        response = client.post(
            client.app.url_path_for("Appointment.send_form"),
            data=appointments_data
        )
        err_msg = (
            "You are trying to book an appointment for existing user with"
            "wrong data."
        )
        assert err_msg in response.text
        setup_test.delete_patient(appointments_data.get("phone"))


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize(
    "appointments_data", ["booking_form"], indirect=True
)
class TestAppointmentEndpointCreatedInfo:
    def test_created_info_returns_ok(
            self, client: TestClient, url_appointment_created: str
    ) -> None:
        response = client.get(url_appointment_created)
        assert response.status_code == status.HTTP_200_OK

    def test_created_info_contains_appointment_info(
            self,
            client: TestClient,
            url_appointment_created: str,
            appointment: Appointment
    ) -> None:
        response = client.get(url_appointment_created)
        soup = BeautifulSoup(response.text, "html.parser")
        appointment_info = [
            appointment_details.text
            for appointment_details
            in soup.find_all("dd")
        ]
        assert str(appointment.id) in appointment_info

    @pytest.mark.parametrize(
        "jwt_token_service", [timedelta(seconds=1)], indirect=True
    )
    def test_attempt_to_access_with_expired_token_redirects_to_main(
            self, client: TestClient, url_appointment_created: str
    ) -> None:
        client.get(url_appointment_created)
        sleep(2)
        response = client.get(url_appointment_created, follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == client.app.url_path_for("main")

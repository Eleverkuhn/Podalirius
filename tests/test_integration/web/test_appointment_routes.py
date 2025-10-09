from datetime import timedelta, datetime
from time import sleep
from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError

from logger.setup import get_logger
from exceptions import DataDoesNotMatch
from utils import SetUpTest
from model.form_models import AppointmentBookingForm
from model.appointment_models import Appointment
from data.patient_data import PatientSQLModel
from tests.test_integration.web.conftest import BaseEndpointTest


@pytest.fixture
def booking_form(test_data: dict, request) -> dict:
    return test_data.get(request.param)


@pytest.fixture
def url_appointment_created(
        client: TestClient, jwt_token_appointment: str
) -> str:
    base = client.app.url_path_for("Appointment.appointment_created")
    return "".join([base, f"?token={jwt_token_appointment}"])


@pytest.mark.parametrize(
    "test_data", ["test_appointments.json"], indirect=True
)
@pytest.mark.usefixtures("test_data")
class TestAppointmentEndpoint(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "get_form": self.client.app.url_path_for(
                "Appointment.get_appointment_form"
            ),
            "send_form": self.client.app.url_path_for(
                "Appointment.create_appointment"
            )
        }

    def test_get_returns_blank_form_for_unlogged_in_user(self) -> None:
        response = self.get_request("get_form")
        soup = BeautifulSoup(response.text, "html.parser")
        form_fields = soup.find_all("input")
        for field in form_fields:
            assert field.get("value") == ""

    @pytest.mark.parametrize(
        "booking_form", ["booking_form"], indirect=True
    )
    def test_appointment_form_redirects_to_main(
            self,
            booking_form: dict,
            setup_test: SetUpTest,
    ) -> None:
        response = self.post_request("send_form", booking_form)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        get_logger().debug(response.headers.get("location"))
        setup_test.delete_patient(booking_form.get("phone"))

    @pytest.mark.parametrize(
        "booking_form", ["booking_form"], indirect=True
    )
    def test_missing_form_field_raises_unprocessable_entity(
            self, booking_form: dict
    ) -> None:
        booking_form.pop("date")
        response = self.post_request("send_form", booking_form)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "booking_form", ["booking_form"], indirect=True
    )
    def test_invalid_pydantyic_field_raises_validation_error(
            self, booking_form: dict
    ) -> None:
        booking_form.update({"last_name": "1232"})
        response = self.post_request("send_form", booking_form)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "booking_form", ["invalid_booking_form"], indirect=True
    )
    def test_invalid_pydantic_field_error_msg_rendered_at_correct_form_field(
            self, booking_form: dict
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            AppointmentBookingForm(**booking_form)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = self.post_request("send_form", booking_form)
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [
            tag.get_text(strip=True)
            for tag
            in soup.find_all("small")
        ]
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)


    @pytest.mark.parametrize(
        "booking_form", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.parametrize(
        "test_entry",
        [(PatientSQLModel, "booking_form")],
        indirect=True
    )
    def test_miss_matching_data_raises_request_validation_error(
            self,
            booking_form: dict,
            setup_test: SetUpTest,
            test_entry: PatientSQLModel
    ) -> None:
        response = self.post_request("send_form", booking_form)
        assert DataDoesNotMatch.default_message in response.text
        setup_test.tear_down(test_entry)

    @pytest.mark.parametrize("patient", ["patient_1"], indirect=True)
    @pytest.mark.parametrize("appointment", ["booking_form"], indirect=True)
    @pytest.mark.parametrize("jwt_token_appointment", [None], indirect=True)
    def test_created_info_returns_ok(self, url_appointment_created) -> None:
        get_logger().debug(url_appointment_created)
        response = self.client.get(url_appointment_created)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("patient", ["patient_1"], indirect=True)
    @pytest.mark.parametrize("appointment", ["booking_form"], indirect=True)
    @pytest.mark.parametrize("jwt_token_appointment", [None], indirect=True)
    def test_created_info_contains_appointment_info(
            self, url_appointment_created, appointment: Appointment
    ) -> None:
        response = self.client.get(url_appointment_created)
        soup = BeautifulSoup(response.text, "html.parser")
        appointment_info = [
            appointment_details.text
            for appointment_details
            in soup.find_all("dd")
        ]
        assert str(appointment.id) in appointment_info

    @pytest.mark.parametrize("patient", ["patient_1"], indirect=True)
    @pytest.mark.parametrize("appointment", ["booking_form"], indirect=True)
    @pytest.mark.parametrize(
        "jwt_token_appointment", [timedelta(seconds=1)], indirect=True
    )
    def test_attempt_to_access_with_expired_token_redirects_to_main(
            self, url_appointment_created
    ) -> None:
        self.client.get(url_appointment_created)
        sleep(2)
        response = self.client.get(
            url_appointment_created, follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self.client.app.url_path_for("main")

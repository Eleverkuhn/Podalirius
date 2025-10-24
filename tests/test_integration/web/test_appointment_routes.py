from datetime import datetime, timedelta
from time import sleep
from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi import status

from logger.setup import get_logger
from utils import SetUpTest
from model.form_models import AppointmentBookingForm
from model.appointment_models import Appointment
from data.patient_data import PatientSQLModel
from tests.test_integration.web.conftest import (
    BaseTestEndpoint, EndpointWithForm
)


class TestAppointmentEndpointGetForm(BaseTestEndpoint):
    base_url = "Appointment.get_form"

    def test_get_returns_blank_form_for_unlogged_in_user(self) -> None:
        response = self.client.get(self._get_url())
        soup = BeautifulSoup(response.text, "html.parser")
        form_fields = soup.find_all("input")
        for field in form_fields:
            assert field.get("value") == ""

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test_form_is_pre_filled_for_logged_in_user(
            self, patient: PatientSQLModel, cookies: dict[str, str]
    ) -> None:
        self.client.cookies = cookies
        response = self.client.get(self._get_url())
        soup = BeautifulSoup(response.text, "html.parser")
        field_values = [
            input_tag.get("value")
            for input_tag
            in soup.find_all("input")
        ]
        patient_dumped = patient.model_dump(exclude=[
            "id", "created_at", "updated_at"
        ])
        patient_dumped.update({
            "birth_date": patient_dumped.get("birth_date").isoformat()
        })
        assert sorted(field_values) == sorted(list(patient_dumped.values()))


class TestAppointmentEndpointSendForm(EndpointWithForm):
    base_url = "Appointment.send_form"

    @override
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_redirects(
            self, appointments_data: dict, setup_test: SetUpTest,
    ) -> None:
        response = self._post_req(appointments_data)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        setup_test.delete_patient(appointments_data.get("phone"))

    @override
    @pytest.mark.parametrize(
        "appointments_data", ["booking_form"], indirect=True
    )
    def test_invalid_form_data_returns_422(
            self, appointments_data: dict
    ) -> None:
        appointments_data.update({"last_name": "1232"})
        super().test_invalid_form_data_returns_422(appointments_data)

    @override
    @pytest.mark.parametrize(
        "appointments_data", ["invalid_booking_form"], indirect=True
    )
    def test_validation_err_msgs_are_rendered_correctly(
            self, appointments_data: dict
    ) -> None:
        super().test_validation_err_msgs_are_rendered_correctly(
            AppointmentBookingForm, appointments_data
        )

    @pytest.mark.parametrize(
        "appointments_data", ["miss_matched_user_data"], indirect=True
    )
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patient")
    def test_miss_matching_data_raises_request_validation_error(
            self, appointments_data: dict, setup_test: SetUpTest,
    ) -> None:
        response = self.client.post(self._get_url(), data=appointments_data)
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
class TestAppointmentEndpointCreatedInfo(BaseTestEndpoint):
    base_url = "Appointment.info"

    def _token_url(self, token: str) -> str:
        return f"{self._get_url()}?token={token}"

    @override
    def test_exists(self, jwt_token_appointment: str) -> None:
        response = self.client.get(self._token_url(jwt_token_appointment))
        assert response.status_code == status.HTTP_200_OK

    def test_created_info_contains_appointment_info(
            self, jwt_token_appointment: str, appointment: Appointment
    ) -> None:
        response = self.client.get(self._token_url(jwt_token_appointment))
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
            self, jwt_token_appointment: str
    ) -> None:
        self.client.get(self._token_url(jwt_token_appointment))
        sleep(2)
        response = self.client.get(
            self._token_url(jwt_token_appointment),
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self._get_url("Main.main")

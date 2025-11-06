from typing import override

import pytest
from fastapi import status, Response
from fastapi.testclient import TestClient

from logger.setup import get_logger
from main import app
from model.appointment_models import AppointmentOuter
from service.auth_services import JWTTokenService
from tests.test_integration.conftest import BasePatientTest, appointment_status
from tests.test_integration.web.conftest import BaseTestEndpoint


@pytest.fixture
def authorized_client(access_token: str) -> TestClient:
    return TestClient(app, cookies={"access_token": access_token})


@pytest.fixture
def access_token(patient_str_id: str) -> str:
    access_token = JWTTokenService().create(patient_str_id)
    return access_token


class BasePatientEndpointTest(BaseTestEndpoint):
    base_url = "PatientAppointment.all"


class BaseAuthorizedPatientEndpointTest(
        BasePatientEndpointTest, BasePatientTest
):
    @override
    @pytest.fixture(autouse=True)
    def setup_method(self, authorized_client: TestClient) -> None:
        self.client = authorized_client


@pytest.mark.usefixtures("patient")
class TestPatientEndpoint(BaseAuthorizedPatientEndpointTest):
    # INFO: has URL parameters
    @override
    def test_exists(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize("appointments", [0], indirect=True)
@pytest.mark.usefixtures("link_services_to_appointments")
class TestPatientEndpointWithAppointments(BaseAuthorizedPatientEndpointTest):
    def test_get_all_displays_all_appointments(
            self, converted_appointments: list[AppointmentOuter]
    ) -> None:
        response = self.client.get(self._get_url())
        self._find_appointment_info_in_response(
            converted_appointments, response
        )

    @pytest.mark.parametrize(
        "filtered_appointments", appointment_status, indirect=True
    )
    def test_get_all_filtered_by_pending_status(
            self, filtered_appointments: list[AppointmentOuter]
    ) -> None:
        appointment_status, appointments = filtered_appointments
        pending_url = "".join(
            [self._get_url(), f"?status={appointment_status}"]
        )
        response = self.client.get(pending_url)
        self._find_appointment_info_in_response(appointments, response)

    def _find_appointment_info_in_response(
        self, appointments: list[AppointmentOuter], response: Response
    ) -> None:
        for appointment in appointments:
            for value in appointment.model_dump().values():
                assert str(value) in response.text


class TestPatientEndpointAnuthorized(BasePatientEndpointTest):
    def test_unauthorized_patient_get_redirected_to_main(self) -> None:
        response = self.client.get(self._get_url(), follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self._get_url("Main.main")

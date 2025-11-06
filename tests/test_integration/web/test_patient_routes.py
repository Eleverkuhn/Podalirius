from typing import override

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from logger.setup import get_logger
from main import app
from model.appointment_models import AppointmentOuter
from service.auth_services import JWTTokenService
from tests.test_integration.conftest import BasePatientTest
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


@pytest.mark.usefixtures("patient")
class TestPatientEndpoint(BasePatientEndpointTest, BasePatientTest):
    # INFO: has URL parameters
    @override
    @pytest.fixture(autouse=True)
    def setup_method(self, authorized_client: TestClient) -> None:
        self.client = authorized_client

    @override
    def test_exists(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
    @pytest.mark.parametrize("appointments", [0], indirect=True)
    @pytest.mark.usefixtures("link_services_to_appointments")
    def test_get_all_displays_all_appointments(
            self, converted_appointments: list[AppointmentOuter]
    ) -> None:
        response = self.client.get(self._get_url())
        for appointment in converted_appointments:
            for value in appointment.model_dump().values():
                assert str(value) in response.text
        get_logger().debug(converted_appointments)
        get_logger().debug(response.text)


class TestPatientEndpointAnuthorized(BasePatientEndpointTest):
    def test_unauthorized_patient_get_redirected_to_main(self) -> None:
        response = self.client.get(self._get_url(), follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self._get_url("Main.main")

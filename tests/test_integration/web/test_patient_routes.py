from typing import override

import pytest
from fastapi import status, Response
from fastapi.testclient import TestClient

from logger.setup import get_logger
from main import app
from model.appointment_models import AppointmentOuter
from model.form_models import RescheduleAppointmentForm
from service.auth_services import JWTTokenService
from tests.test_integration.conftest import BasePatientTest, appointment_status
from tests.test_integration.web.conftest import (
    BaseTestEndpoint, EndpointWithForm
)


@pytest.fixture
def authorized_client(access_token: str) -> TestClient:
    return TestClient(app, cookies={"access_token": access_token})


@pytest.fixture
def access_token(patient_str_id: str) -> str:
    access_token = JWTTokenService().create(patient_str_id)
    return access_token


@pytest.fixture
def converted_appointment(
        converted_appointments: list[AppointmentOuter],
        request: pytest.FixtureRequest
) -> AppointmentOuter:
    converted_appointment = converted_appointments[request.param]
    return converted_appointment


class BasePatientEndpointTest(BaseTestEndpoint):
    base_url = "PatientAppointment.all"


class BaseAuthorizedPatientEndpointTest(
        BasePatientEndpointTest, BasePatientTest
):
    @override
    @pytest.fixture(autouse=True)
    def setup_method(self, authorized_client: TestClient) -> None:
        self.client = authorized_client


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize("appointments", [0], indirect=True)
@pytest.mark.usefixtures("link_services_to_appointments")
class BasePatientAppointmentTest(BaseAuthorizedPatientEndpointTest):
    appointment_url = "PatientAppointment.appointment"

    @override
    def _get_url(
            self,
            name: str | None = None,
            id: int | str | None = None
    ) -> None:
        # FIX: rework `_get_url in general`
        if name:
            return self.client.app.url_path_for(name)
        elif id:
            get_logger().debug("Inside elif")
            url = self.client.app.url_path_for(self.appointment_url, id=id)
            get_logger().debug(url)
            return url
        return self.client.app.url_path_for(self.base_url)


@pytest.mark.usefixtures("patient")
class TestPatientEndpoint(BaseAuthorizedPatientEndpointTest):
    # INFO: has URL parameters
    @override
    def test_exists(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_200_OK


class TestPatientEndpointWithAppointments(BasePatientAppointmentTest):
    @pytest.mark.parametrize(
        "filtered_appointments", appointment_status, indirect=True
    )
    def test_get_all_filtered_by_status(
            self, filtered_appointments: list[AppointmentOuter]
    ) -> None:
        appointment_status, appointments = filtered_appointments
        pending_url = "".join(
            [self._get_url(), f"?appointment_status={appointment_status}"]
        )
        response = self.client.get(pending_url)
        for appointment in appointments:
            self._find_appointment_info_in_response(appointment, response)

    @pytest.mark.parametrize("converted_appointment", [0], indirect=True)
    def test_get_displays_appointment_info(
            self, converted_appointment: AppointmentOuter
    ) -> None:
        response = self.client.get(self._get_url(id=converted_appointment.id))
        self._find_appointment_info_in_response(converted_appointment, response)

    def _find_appointment_info_in_response(
            self, appointment: AppointmentOuter, response: Response
    ) -> None:
        for value in appointment.model_dump().values():
            assert str(value) in response.text


@pytest.mark.parametrize("converted_appointment", [0], indirect=True)
@pytest.mark.usefixtures("converted_appointment")
class TestPatientAppointmentInfoUpdate(BasePatientAppointmentTest):
    @pytest.fixture(autouse=True)
    def _converted_appointment(
            self, converted_appointment: AppointmentOuter
    ) -> None:
        self.converted_appointment = converted_appointment

    def test_cancel_is_succeed(self) -> None:
        url = self._get_url(id=self.converted_appointment.id)
        get_logger().debug(type(url))
        response = self.client.get(
            self._get_url(id=self.converted_appointment.id)
        )
        assert "pending" in response.text
        response = self.client.patch(
            self._get_url(
                id=self.converted_appointment.id), follow_redirects=True
        )
        get_logger().debug(response.text)
        assert "cancelled" in response.text

    def test_update_is_succeed(
            self,
            reschedule_appointment_form: RescheduleAppointmentForm
    ) -> None:
        url = self._get_url(id=self.converted_appointment.id)
        response = self.client.get(url)
        assert self.converted_appointment.date.isoformat() in response.text
        assert self.converted_appointment.time.isoformat() in response.text
        dumped_form = reschedule_appointment_form.model_dump()
        dumped_form.update(
            {
                "date": reschedule_appointment_form.date.isoformat(),
                "time": reschedule_appointment_form.time.isoformat()
            }
        )
        response = self.client.put(url, json=dumped_form)
        assert reschedule_appointment_form.date.isoformat() in response.text
        assert reschedule_appointment_form.time.isoformat() in response.text


class TestPatientEndpointAnuthorized(BasePatientEndpointTest):
    def test_unauthorized_patient_get_redirected_to_main(self) -> None:
        response = self.client.get(self._get_url(), follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self._get_url("Main.main")

from typing import override

import pytest
from fastapi import status, Response
from fastapi.testclient import TestClient
from pydantic import BaseModel

from logger.setup import get_logger
from model.patient_models import PatientCreate
from model.appointment_models import AppointmentOuter, AppointmentDateTime
from service.auth_services import JWTTokenService
from data.base_data import BaseSQLModel
from data.sql_models import Patient
from data.patient_data import PatientCRUD
from tests.test_integration.conftest import BasePatientTest, appointment_status
from tests.test_integration.web.conftest import (
    BaseTestEndpoint, BaseProtectedEndpointTest
)


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


@pytest.fixture
def patient_public(patient: Patient) -> PatientCreate:
    patient_public = PatientCreate(**patient.model_dump())
    return patient_public


@pytest.fixture
def patient_update_data(patient_update_info: PatientCreate) -> dict:
    patient_dumped = patient_update_info.model_dump()
    PatientCRUD.convert_birth_date_to_str(patient_dumped)
    return patient_dumped


class BasePatientEndpointTest(BaseTestEndpoint):
    base_url = "PatientAppointment.all"
    param = "id"

    def _info_is_displayed_correctly(
            self, model: BaseModel | BaseSQLModel, response: Response
    ) -> None:
        for value in model.model_dump().values():
            get_logger().debug(value)
            assert str(value) in response.text


class BaseAuthorizedPatientEndpointTest(
        BaseProtectedEndpointTest,
        BasePatientEndpointTest,
        BasePatientTest
):
    pass


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize("appointments", [0], indirect=True)
@pytest.mark.usefixtures("link_services_to_appointments")
class BasePatientAppointmentTest(BaseAuthorizedPatientEndpointTest):
    base_url = "PatientAppointment.appointment"


@pytest.mark.usefixtures("patient")
class TestPatientEndpoint(BaseAuthorizedPatientEndpointTest):
    # INFO: has URL parameters
    @override
    def test_exists(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_200_OK


class TestPatientAppointmentAll(BasePatientAppointmentTest):
    base_url = "PatientAppointment.all"

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
            self._info_is_displayed_correctly(appointment, response)


@pytest.mark.parametrize("converted_appointment", [0], indirect=True)
@pytest.mark.usefixtures("converted_appointment")
class TestPatientAppointmentInfo(BasePatientAppointmentTest):
    @pytest.fixture(autouse=True)
    def _converted_appointment(
            self, converted_appointment: AppointmentOuter
    ) -> None:
        self.converted_appointment = converted_appointment

    # @pytest.mark.parametrize("converted_appointment", [0], indirect=True)
    def test_get_displays_appointment_info(self) -> None:
        response = self.client.get(self._get_url(self.converted_appointment.id))
        self._info_is_displayed_correctly(self.converted_appointment, response)

    def test_cancel_is_succeed(self) -> None:
        url = self._get_url(self.converted_appointment.id)
        get_logger().debug(type(url))
        response = self.client.get(
            self._get_url(self.converted_appointment.id)
        )
        assert "pending" in response.text
        response = self.client.patch(
            self._get_url(self.converted_appointment.id),
            follow_redirects=True
        )
        get_logger().debug(response.text)
        assert "cancelled" in response.text

    def test_update_is_succeed(
            self,
            reschedule_appointment_form: AppointmentDateTime
    ) -> None:
        url = self._get_url(self.converted_appointment.id)
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
        redirected = self._get_url(path="Main.main")
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == redirected


class TestPatientInfoEndpoint(TestPatientEndpoint):
    base_url = "PatientInfo.info"

    @pytest.fixture(autouse=True)
    def _patient(self, patient_public: PatientCreate) -> None:
        self.patient = patient_public

    def test_get_displays_patient_info(self) -> None:
        response = self.client.get(self._get_url())
        self._info_is_displayed_correctly(self.patient, response)

    def test_update_is_succeed(
            self,
            patient_update_data: dict,
            patient_update_info: PatientCreate
    ) -> None:
        response = self.client.get(self._get_url())
        self._info_is_displayed_correctly(self.patient, response)
        response = self.client.put(self._get_url(), data=patient_update_data)
        get_logger().debug(response.text)
        self._info_is_displayed_correctly(patient_update_info, response)

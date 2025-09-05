from typing import override

import pytest
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from model import (
    appointment_models,
    base_models,
    doctor_models,
    patient_models,
    service_models,
    specialty_models
)


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def phone_number_form_data() -> dict[str, str]:
    return {"phone": "9999999999"}


class BaseEndpointTest:
    model: None | base_models.AbstractModel = None
    urls: None | dict[str, str] = None

    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client
        self.model = self.get_model()
        self.urls = self.get_urls()

    def get_model(self) -> base_models.AbstractModel:
        return self.model

    def get_urls(self) -> dict[str, str]:
        return self.urls

    def test_endpoints_exist(self) -> None:
        for url in self.urls.values():
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK


class TestMain(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {"main": self.client.app.url_path_for("main")}


class TestSpecialties(BaseEndpointTest):
    # INFO: has URL parameters
    @override
    def get_model(self) -> specialty_models.Specialty:
        return specialty_models.Specialty

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "specialties": self.client.app.url_path_for(
                "Specialty.all_specialties"),
            "specialty": self.client.app.url_path_for(
                "Specialty.specialty", title="1")
        }


class TestServices(BaseEndpointTest):
    # INFO: has URL parameters
    @override
    def get_model(self) -> service_models.Service:
        return service_models.Service

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "service": self.client.app.url_path_for("Service.service", title="1")
        }


class TestDoctorEndpoint(BaseEndpointTest):
    # INFO: has URL parameter
    @override
    def get_model(self) -> doctor_models.Doctor:
        return doctor_models.Doctor

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "doctor": self.client.app.url_path_for("Doctor.doctor", id=1)
        }


class TestAppointments(BaseEndpointTest):
    @override
    def get_model(self) -> appointment_models.Appointment:
        return appointment_models.Appointment

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "get_form": self.client.app.url_path_for("Appointment.get_appointment_form"),
            "send_form": self.client.app.url_path_for("Appointment.create_appointment")
        }

    @override
    def test_endpoints_exist(self) -> None:
        # TODO: change this
        pass

    def test_appointment_form_endpoint_exists(self) -> None:
        response = self.client.get(self.urls.get("get_form"))
        assert response.status_code == status.HTTP_200_OK

    def test_appointment_form_redirects_to_main(self) -> None:
        response = self.client.post(
            self.urls.get("send_form"),
            follow_redirects=False)
        location = response.headers.get("location")
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert location == self.client.app.url_path_for("main")


class TestAuthEndpoint(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "login_form": self.client.app.url_path_for("Login.login_form"),
            "verify_code_form": self.client.app.url_path_for("VerifyCode.verify_code_form"),
        }

    def test_sending_login_form_redirects_correctly(
            self, phone_number_form_data: dict[str, str]) -> None:
        response = self.client.post(
            self.urls.get("login_form"),
            data=phone_number_form_data,
            follow_redirects=False,
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self.client.app.url_path_for("VerifyCode.verify_code_form")

    def test_verify_code_form_post_is_allowed(self) -> None:
        response = self.client.post(self.urls.get("verify_code_form"))
        assert response.status_code == status.HTTP_200_OK


class TestPatientEndpoint(BaseEndpointTest):
    # INFO: has URL parameters

    @override
    def get_model(self) -> patient_models.Patient:
        return patient_models.Patient

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "appointments": self.client.app.url_path_for("PatientAppointment.all_appointments"),
            "appointment": self.client.app.url_path_for("PatientAppointment.appointment", id=1),
            "info": self.client.app.url_path_for("PatientInfo.info")
        }

from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from fastapi import status, Response
from pydantic import ValidationError

from model.form_models import AppointmentBookingForm
from model import (
    appointment_models,
    base_models,
    doctor_models,
    patient_models,
    service_models,
    specialty_models
)

type FormData = dict[str, str | int]


@pytest.fixture
def phone_number_form_data() -> FormData:
    return {"phone": "9999999999"}


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

    def get_request(self, url_name: str) -> Response:
        return self.client.get(self.urls.get(url_name))

    def post_request(
            self, url_name: str, data: FormData, follow_redirects: bool = False) -> Response:
        return self.client.post(
            self.urls.get(url_name),
            data=data,
            follow_redirects=follow_redirects
        )

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


class TestAppointment(BaseEndpointTest):
    @override
    def get_model(self) -> appointment_models.Appointment:
        return appointment_models.Appointment

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


class TestAuthEndpoint(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "login_form": self.client.app.url_path_for("Login.login_form"),
            "verify_code_form": self.client.app.url_path_for(
                "VerifyCode.verify_code_form"),
        }

    def test_sending_login_form_redirects_correctly(
            self, phone_number_form_data: FormData) -> None:
        response = self.post_request(
            "login_form", phone_number_form_data
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self.client.app.url_path_for("VerifyCode.verify_code_form")

    def test_verify_code_form_post_is_allowed(self) -> None:  # TODO: what's this
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
            "appointments": self.client.app.url_path_for(
                "PatientAppointment.all_appointments"),
            "appointment": self.client.app.url_path_for(
                "PatientAppointment.appointment", id=1),
            "info": self.client.app.url_path_for(
                "PatientInfo.info")
        }

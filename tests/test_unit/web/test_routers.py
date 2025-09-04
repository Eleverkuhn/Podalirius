import logging
from abc import ABC

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
from web import (
    appointment_routes,
    doctor_routes,
    patient_routes,
    service_routes,
    specialty_routes,
    index_routes,
    auth_routes
)


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)


class BaseEndpoint(ABC):
    model: base_models.AbstractModel
    prefixes: list[str]

    def test_endpoint_exists(self, client: TestClient) -> None:
        logger = logging.getLogger("tests")
        for prefix in self.prefixes:
            logger.warning(f"PREFIX: {prefix}")
            response = client.get(prefix)
            assert response.status_code == status.HTTP_200_OK


class BasePostEndpoint(BaseEndpoint):
    def test_post_allowed(self, client: TestClient) -> None:
        for prefix in self.prefixes:
            response = client.post(prefix)
            assert response.status_code == status.HTTP_201_CREATED


class TestMain(BaseEndpoint):
    prefixes = [index_routes.router.prefix]


class TestSpecialties(BaseEndpoint):
    # INFO: has URL parameters
    model = specialty_models.Specialty
    prefixes = [specialty_routes.router.prefix]


class TestServices(BaseEndpoint):
    # INFO: has URL parameters
    model = service_models.Service
    prefixes = [service_routes.router.prefix]


class TestDoctors(BaseEndpoint):
    # INFO: has URL parameters
    model = doctor_models.Doctor
    prefixes = [doctor_routes.router.prefix]


class TestAppointments(BasePostEndpoint):
    model = appointment_models.Appointment
    prefixes = [appointment_routes.router.prefix]


class TestAuth(BasePostEndpoint):
    prefixes = [auth_routes.login_router.prefix, auth_routes.verify_code_router.prefix]


class TestPatients(BaseEndpoint):
    # INFO: has URL parameters
    model = patient_models.Patient
    prefixes = [
        patient_routes.patient_appointments_router.prefix,
        patient_routes.patient_info_router.prefix
    ]

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from logger.setup import get_logger
from service.auth_services import JWTTokenService
from data.patient_data import PatientCRUD, PatientSQLModel


class TestPatientEndpoint:
    # INFO: has URL parameters
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patient")
    def test_authorization_is_succeed(
        self, client: TestClient, patient: PatientSQLModel
    ) -> None:
        access_token = JWTTokenService().create(
            PatientCRUD.uuid_to_str(patient.id)
        )
        response = client.get(
            client.app.url_path_for("PatientAppointment.all"),
            cookies={"access_token": access_token}
        )
        get_logger().debug(response.text)
        assert response.status_code == status.HTTP_200_OK

    def test_authorization_is_failed(self, client: TestClient) -> None:
        response = client.get(
            client.app.url_path_for("PatientAppointment.all")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

from typing import override

import pytest
from fastapi import status

from service.auth_services import JWTTokenService
from data.patient_data import PatientCRUD, PatientSQLModel
from tests.test_integration.web.conftest import BaseTestEndpoint


class TestPatientEndpoint(BaseTestEndpoint):
    # INFO: has URL parameters
    base_url = "PatientAppointment.all"

    @override
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patient")
    def test_exists(self, patient: PatientSQLModel) -> None:
        access_token = JWTTokenService().create(
            PatientCRUD.uuid_to_str(patient.id)
        )
        response = self.client.get(
            self._get_url(),
            cookies={"access_token": access_token}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_authorization_is_failed(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

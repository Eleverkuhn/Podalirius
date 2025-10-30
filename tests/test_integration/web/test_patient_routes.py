from typing import override

import pytest
from fastapi import status

from service.auth_services import JWTTokenService
from data.patient_data import PatientCRUD, Patient
from tests.test_integration.web.conftest import BaseTestEndpoint


class TestPatientEndpoint(BaseTestEndpoint):
    # INFO: has URL parameters
    base_url = "PatientAppointment.all"

    @override
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("patient")
    def test_exists(self, patient: Patient) -> None:
        patient_id = PatientCRUD.uuid_to_str(patient.id)
        access_token = JWTTokenService().create(patient_id)
        response = self.client.get(
            self._get_url(),
            cookies={"access_token": access_token}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_unauthorized_patient_get_redirected_to_main(self) -> None:
        response = self.client.get(self._get_url(), follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self._get_url("Main.main")

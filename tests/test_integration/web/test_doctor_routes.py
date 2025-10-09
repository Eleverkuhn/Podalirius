import pytest
from fastapi import status
from fastapi.testclient import TestClient

from logger.setup import get_logger
from data import sql_models


class TestDoctorEndpoint:  # INFO: has URL parameter
    @pytest.mark.parametrize(
        "get_all", [(sql_models.Doctor, sql_models.Doctor)], indirect=True
    )
    def test_exists(self, client: TestClient, get_all) -> None:
        for doctor in get_all:
            response = client.get(client.app.url_path_for(
                "Doctor.doctor", id=doctor.id
            ))
            assert response.status_code == status.HTTP_200_OK

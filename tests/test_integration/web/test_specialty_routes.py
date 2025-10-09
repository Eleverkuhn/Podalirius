import pytest
from fastapi import status
from fastapi.testclient import TestClient

from data import sql_models


class TestSpecialtyEndpoint:  # INFO: has URL parameters
    def test_all_specialties_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Specialty.all"))
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "get_all",
        [(sql_models.Specialty, sql_models.Specialty)],
        indirect=True
    )
    def test_exists(self, client: TestClient, get_all) -> None:
        for specialty in get_all:
            response = client.get(client.app.url_path_for(
                "Specialty.specialty", title=specialty.title
            ))
            assert response.status_code == status.HTTP_200_OK

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from data import sql_models
from data.crud import BaseCRUD


class TestServiceEndpoint:  # INFO: has URL parameters
    @pytest.mark.parametrize(
        "get_all", [(sql_models.Service, sql_models.Service)], indirect=True
    )
    def test_exists(self, client: TestClient, get_all) -> None:
        for service in get_all:
            response = client.get(client.app.url_path_for(
                "Service.service", title=service.title
            ))
            assert response.status_code == status.HTTP_200_OK

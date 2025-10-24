from typing import override

from fastapi import status
from sqlmodel import Session

from data.sql_models import Specialty
from tests.test_integration.web.conftest import EndpointWithURLParams


class TestSpecialtyEndpoint(EndpointWithURLParams):
    # INFO: has URL parameters
    base_url = "Specialty.specialty"
    param = "title"
    sql_model = Specialty

    def test_all_specialties_exists(self) -> None:
        response = self.client.get(self._get_url("Specialty.all"))
        assert response.status_code == status.HTTP_200_OK

    @override
    def test_multiple_exist(self, session: Session) -> None:
        super().test_multiple_exist(session)

from typing import override

import pytest
from fastapi import status
from sqlmodel import Session, Sequence

from logger.setup import get_logger
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

    def test_all_specialties_render_correctly(
            self, specialties: Sequence[Specialty]
    ) -> None:
        response = self.client.get(self._get_url(path="Specialty.all"))
        for specialty in specialties:
            assert specialty.title in response.text

    @pytest.mark.parametrize("specialty", [0], indirect=True)
    @pytest.mark.usefixtures("doctors")
    def test_detailed_info_render_correctly(
            self, specialty: Specialty
    ) -> None:
        response = self.client.get(self._get_url(param=specialty.title))
        assert specialty.title in response.text
        for doctor in specialty.doctors:
            assert doctor.full_name in response.text

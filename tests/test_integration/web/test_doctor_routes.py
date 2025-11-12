from typing import override

import pytest
from fastapi import status
from sqlmodel import Session

from logger.setup import get_logger
from data.sql_models import Doctor
from tests.test_integration.web.conftest import (
    EndpointWithURLParams, BaseTestEndpoint
)


class TestDoctorEndpoint(EndpointWithURLParams):
    # INFO: has URL parameter
    base_url = "Doctor.doctor"
    param = "id"
    sql_model = Doctor

    @override
    def test_multiple_exist(self, session: Session) -> None:
        super().test_multiple_exist(session)

    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test_detailed_doctor_info_render_correctly(
            self, doctor: Doctor
    ) -> None:
        response = self.client.get(self._get_url(param=doctor.id))
        assert doctor.full_name in response.text


@pytest.mark.parametrize("doctor", [0], indirect=True)
class TestDoctorScheduleEndpoint(BaseTestEndpoint):
    base_url = "Doctor.schedule"

    @pytest.fixture(autouse=True)
    def set_doctor(self, doctor: Doctor) -> None:
        self.doctor = doctor

    @property
    def path(self) -> str:
        path = self.client.app.url_path_for(self.base_url, id=self.doctor.id)
        return path

    def test_schedule_exists(self) -> None:
        response = self.client.get(self.path)
        assert response.status_code == status.HTTP_200_OK

    def test_schedule(self) -> None:
        response = self.client.get(self.path)
        assert response

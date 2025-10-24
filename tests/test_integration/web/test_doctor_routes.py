from typing import override

from sqlmodel import Session

from data.sql_models import Doctor
from tests.test_integration.web.conftest import EndpointWithURLParams


class TestDoctorEndpoint(EndpointWithURLParams):
    # INFO: has URL parameter
    base_url = "Doctor.doctor"
    param = "id"
    sql_model = Doctor

    @override
    def test_multiple_exist(self, session: Session) -> None:
        super().test_multiple_exist(session)

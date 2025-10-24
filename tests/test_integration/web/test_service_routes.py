from typing import override

from sqlmodel import Session

from data.sql_models import Service
from tests.test_integration.web.conftest import EndpointWithURLParams


class TestServiceEndpoint(EndpointWithURLParams):
    # INFO: has URL parameters
    base_url = "Service.service"
    param = "title"
    sql_model = Service

    @override
    def test_multiple_exist(self, session: Session) -> None:
        super().test_multiple_exist(session)

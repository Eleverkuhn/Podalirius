from typing import override

from sqlmodel import Session

from data import sql_models
from tests.test_integration.web.conftest import EndpointWithURLParams


class TestServiceEndpoint(EndpointWithURLParams):
    # INFO: has URL parameters
    base_url = "Service.service"
    param = "title"
    sql_model = sql_models.Service

    @override
    def test_multiple_exist(self, session: Session) -> None:
        super().test_multiple_exist(session)

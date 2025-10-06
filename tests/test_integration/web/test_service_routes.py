from typing import override

from tests.test_integration.web.conftest import BaseEndpointTest


class TestServiceEndpoint(BaseEndpointTest):
    # INFO: has URL parameters

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "service": self.client.app.url_path_for("Service.service", title="1")
        }

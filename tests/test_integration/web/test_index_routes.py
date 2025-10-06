from typing import override

from tests.test_integration.web.conftest import BaseEndpointTest


class TestIndex(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {"main": self.client.app.url_path_for("main")}

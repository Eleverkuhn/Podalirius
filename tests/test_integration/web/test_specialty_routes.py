from typing import override

from tests.test_integration.web.conftest import BaseEndpointTest


class TestSpecialtyEndpoint(BaseEndpointTest):
    # INFO: has URL parameters

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "specialties": self.client.app.url_path_for(
                "Specialty.all_specialties"),
            "specialty": self.client.app.url_path_for(
                "Specialty.specialty", title="1")
        }

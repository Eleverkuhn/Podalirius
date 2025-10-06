from typing import override

from tests.test_integration.web.conftest import BaseEndpointTest


class TestDoctorEndpoint(BaseEndpointTest):
    # INFO: has URL parameter

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "doctor": self.client.app.url_path_for("Doctor.doctor", id=1)
        }

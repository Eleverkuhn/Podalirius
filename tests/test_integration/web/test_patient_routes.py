from typing import override

from tests.test_integration.web.conftest import BaseEndpointTest


class TestPatientEndpoint(BaseEndpointTest):
    # INFO: has URL parameters

    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "appointments": self.client.app.url_path_for(
                "PatientAppointment.all_appointments"),
            "appointment": self.client.app.url_path_for(
                "PatientAppointment.appointment", id=1),
            "info": self.client.app.url_path_for(
                "PatientInfo.info")
        }

from logger.setup import get_logger
from data.sql_models import Service
from tests.test_integration.web.conftest import BaseTestEndpoint


class TestServiceEndpoint(BaseTestEndpoint):
    base_url = "Service.lab_tests"

    def test_get_lab_tests_renders_correctly(
            self, lab_tests: list[Service]
    ) -> None:
        url = self._get_url()
        get_logger().debug(url)
        response = self.client.get(self._get_url())
        get_logger().debug(response)
        for test in lab_tests:
            assert test.title in response.text
            assert str(int(test.price)) in response.text
        assert lab_tests
        get_logger().debug(lab_tests)

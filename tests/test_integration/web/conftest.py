import pytest
from fastapi.testclient import TestClient
from fastapi import status, Response

from main import app

type FormData = dict[str, str | int]


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)


class BaseEndpointTest:
    urls: None | dict[str, str] = None

    @pytest.fixture(autouse=True)
    def setup(self, client: TestClient) -> None:
        self.client = client
        self.urls = self.get_urls()

    def get_urls(self) -> dict[str, str]:
        return self.urls

    def get_request(self, url_name: str) -> Response:
        return self.client.get(self.urls.get(url_name))

    def post_request(
            self, url_name: str, data: FormData, follow_redirects: bool = False) -> Response:
        return self.client.post(
            self.urls.get(url_name),
            data=data,
            follow_redirects=follow_redirects
        )

    def test_endpoints_exist(self) -> None:
        for url in self.urls.values():
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK

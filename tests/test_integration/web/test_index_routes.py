from fastapi import status
from fastapi.testclient import TestClient


class TestIndex:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Main.main"))
        assert response.status_code == status.HTTP_200_OK

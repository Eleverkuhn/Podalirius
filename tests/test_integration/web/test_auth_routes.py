from fastapi import status
from fastapi.testclient import TestClient


class TestLoginEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Login.form"))
        assert response.status_code == status.HTTP_200_OK

    def test_login_form_redirects_to_verify_code_page_on_success(
            self, client: TestClient
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"),
            data={"phone": "9999999999"},
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == client.app.url_path_for("VerifyCode.form")


class TestVerifyCodeEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("VerifyCode.form"))
        assert response.status_code == status.HTTP_200_OK

    def test_post_is_allowed(self, client: TestClient) -> None:
        response = client.post(client.app.url_path_for("VerifyCode.form"))
        assert response.status_code == status.HTTP_201_CREATED

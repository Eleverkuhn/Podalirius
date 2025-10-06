from typing import override

import pytest
from fastapi import status

from tests.test_integration.web.conftest import BaseEndpointTest

type FormData = dict[str, str | int]


@pytest.fixture
def phone_number_form_data() -> FormData:
    return {"phone": "9999999999"}


class TestAuthEndpoint(BaseEndpointTest):
    @override
    def get_urls(self) -> dict[str, str]:
        return {
            "login_form": self.client.app.url_path_for("Login.login_form"),
            "verify_code_form": self.client.app.url_path_for(
                "VerifyCode.verify_code_form"),
        }

    def test_sending_login_form_redirects_correctly(
            self, phone_number_form_data: FormData) -> None:
        response = self.post_request(
            "login_form", phone_number_form_data
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == self.client.app.url_path_for("VerifyCode.verify_code_form")

    def test_verify_code_form_post_is_allowed(self) -> None:  # TODO: what's this
        response = self.client.post(self.urls.get("verify_code_form"))
        assert response.status_code == status.HTTP_200_OK

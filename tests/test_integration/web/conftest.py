from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from fastapi import status
from pydantic import ValidationError
from sqlmodel import Session

from main import app
from model.base_models import AbstractModel
from data.base_data import BaseSQLModel, BaseCRUD


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def authorized_client(access_token: str) -> TestClient:
    return TestClient(app, cookies={"access_token": access_token})


class BaseTestEndpoint:
    base_url: str
    param: str

    @pytest.fixture(autouse=True)
    def setup_method(self, client: TestClient) -> None:
        self.client = client

    def _get_url(
            self,
            param: str | int | None = None,
            path: str | None = None
    ) -> str:
        if hasattr(self, "param") and param:
            return self._get_parametrized_url(param)
        elif path:
            return self._get_different_url(path)
        else:
            return self._get_default_url()

    def _get_parametrized_url(self, param: str | int) -> str:
        url = self.client.app.url_path_for(
            self.base_url, **{self.param: param}
        )
        return url

    def _get_different_url(self, path: str) -> str:
        url = self.client.app.url_path_for(path)
        return url

    def _get_default_url(self) -> str:
        url = self.client.app.url_path_for(self.base_url)
        return url


class BaseProtectedEndpointTest(BaseTestEndpoint):
    @override
    @pytest.fixture(autouse=True)
    def setup_method(self, authorized_client: TestClient) -> None:
        self.client = authorized_client


class EndpointWithForm(BaseTestEndpoint):
    def test_exists(self) -> None:
        response = self.client.get(self._get_url())
        assert response.status_code == status.HTTP_200_OK

    def test_redirects(self, data: dict[str, str], destination: str) -> None:
        response = self._post_req(data)
        redirected = self._get_url(path=destination)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == redirected

    def test_invalid_form_data_returns_422(
            self, invalid_data: dict[str, str]
    ) -> None:
        response = self.client.post(
            self._get_url(), data=invalid_data, follow_redirects=False
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_err_msgs_are_rendered_correctly(
            self, form: type[AbstractModel], invalid_data: dict[str, str]
    ) -> None:
        raised_errors = self._get_form_errors(form, invalid_data)
        response = self.client.post(self._get_url(), data=invalid_data)
        error_msgs = self._find_errors(response)
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)

    def _get_form_errors(
            self, form: type[AbstractModel], data: dict[str, str]
    ) -> list[str]:
        with pytest.raises(ValidationError) as exc:
            form(**data)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        return raised_errors

    def _find_errors(self, response) -> list[str]:
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [
            tag.get_text(strip=True)
            for tag
            in soup.find_all("small")
        ]
        return error_msgs

    def _post_req(self, data: dict[str, str]):
        response = self.client.post(
            self._get_url(), data=data, follow_redirects=False
        )
        return response


class EndpointWithURLParams(BaseTestEndpoint):
    param: str
    sql_model: type[BaseSQLModel]

    def test_multiple_exist(self, session: Session) -> None:
        for entry in self._get_all_entries(session):
            param_value = getattr(entry, self.param)
            response = self.client.get(
                self.client.app.url_path_for(
                    self.base_url,
                    **{self.param: param_value}
                )
            )
            assert response.status_code == status.HTTP_200_OK

    def _get_all_entries(self, session: Session) -> list[BaseCRUD]:
        return BaseCRUD(session, self.sql_model, self.sql_model).get_all()

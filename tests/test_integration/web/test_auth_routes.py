import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from bs4 import BeautifulSoup

from logger.setup import get_logger
from utils import SetUpTest
from model.form_models import PhoneForm
from data.patient_data import PatientCRUD


@pytest.fixture
def login_data(phone_form: PhoneForm) -> dict[str, str]:
    return phone_form.model_dump()


@pytest.fixture
def invalid_login_data(login_data: dict[str, str]) -> dict[str, str]:
    login_data.update({"phone": "wqeqe"})
    return login_data


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("patients_data")
class TestLoginEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Login.form"))
        assert response.status_code == status.HTTP_200_OK

    def test_login_form_redirects_to_verify_code_page_on_success(
            self, client: TestClient, login_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=login_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == client.app.url_path_for("VerifyCode.form")

    def test_login_form_raises_unprocessable_entity_for_invalid_number(
            self, client: TestClient, invalid_login_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=invalid_login_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_field_err_msgs_are_rendered(
            self, client: TestClient, invalid_login_data: dict[str, str]
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            PhoneForm(**invalid_login_data)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=invalid_login_data
        )
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [
            tag.get_text(strip=True)
            for tag
            in soup.find_all("small")
        ]
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)

    def test_otp_code_is_created(
            self,
            client: TestClient,
            login_data: dict[str, str],
            setup_test: SetUpTest,
            patient_crud: PatientCRUD
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"), 
            data=login_data,
            follow_redirects=False
        )
        patient_db = patient_crud.get_by_phone(login_data.get("phone"))
        otp_code = setup_test.find_otp_code_by_patient_id(patient_db.id)
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert otp_code.patient_id == patient_db.id
        setup_test.delete_patient(login_data.get("phone"))


class TestVerifyCodeEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("VerifyCode.form"))
        assert response.status_code == status.HTTP_200_OK

    def test_post_is_allowed(self, client: TestClient) -> None:
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data={"value": "000000"}
        )
        assert response.status_code == status.HTTP_201_CREATED

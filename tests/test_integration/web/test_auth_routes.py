import pytest
from fastapi import status
from fastapi.testclient import TestClient
from pydantic import ValidationError
from bs4 import BeautifulSoup

from logger.setup import get_logger
from model.form_models import PhoneForm, OTPCodeForm
from data.auth_data import OTPCodeRedis


@pytest.fixture
def phone_data(phone_form: PhoneForm) -> dict[str, str]:
    return phone_form.model_dump()


@pytest.fixture
def invalid_phone_data(phone_data: dict[str, str]) -> dict[str, str]:
    phone_data.update({"phone": "invalid"})
    return phone_data


@pytest.fixture
def otp_code_data(otp_code_form: OTPCodeForm) -> dict[str, str]:
    return otp_code_form.model_dump()


@pytest.fixture
def invalid_otp_code_data(otp_code_data: dict[str, str]) -> dict[str, str]:
    otp_code_data.update({"phone": "invalid", "code": "invalid"})
    return otp_code_data


@pytest.fixture
def mismatched_otp_code_data(otp_code_data: dict[str, str]) -> dict[str, str]:
    otp_code_data.update({"code": "000000"})
    return otp_code_data


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("patients_data")
class TestLoginEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("Login.form"))
        assert response.status_code == status.HTTP_200_OK

    def test_login_form_redirects_to_verify_code_page_on_success(
            self, client: TestClient, phone_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=phone_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == client.app.url_path_for(
            "VerifyCode.form"
        )

    def test_login_form_raises_unprocessable_entity_for_invalid_number(
            self, client: TestClient, invalid_phone_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=invalid_phone_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_field_err_msgs_are_rendered(
            self, client: TestClient, invalid_phone_data: dict[str, str]
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            PhoneForm(**invalid_phone_data)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = client.post(
            client.app.url_path_for("Login.form"),
            data=invalid_phone_data
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
            phone_data: dict[str, str],
            otp_redis: OTPCodeRedis
    ) -> None:
        response = client.post(
            client.app.url_path_for("Login.form"), 
            data=phone_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert otp_redis.get(phone_data.get("phone"))


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("patients_data")
class TestVerifyCodeEndpoint:
    def test_exists(self, client: TestClient) -> None:
        response = client.get(client.app.url_path_for("VerifyCode.form"))
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_post_redirects_to_all_patient_appointments(
            self, client: TestClient, otp_code_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=otp_code_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers.get("location") == client.app.url_path_for(
            "PatientAppointment.all"
        )

    def test_raises_unprocessable_entity_with_invalid_form_data(
            self, client: TestClient, invalid_otp_code_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=invalid_otp_code_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_field_err_msgs_are_rendered(
            self, client: TestClient, invalid_otp_code_data: dict[str, str]
    ) -> None:
        with pytest.raises(ValidationError) as exc:
            OTPCodeForm(**invalid_otp_code_data)
        raised_errors = [error.get("msg") for error in exc.value.errors()]
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=invalid_otp_code_data
        )
        soup = BeautifulSoup(response.text, "html.parser")
        error_msgs = [
            tag.get_text(strip=True)
            for tag
            in soup.find_all("small")
        ]
        get_logger().debug(raised_errors)
        get_logger().debug(error_msgs)
        assert error_msgs is not None
        assert sorted(raised_errors) == sorted(error_msgs)

    @pytest.mark.usefixtures("otp_code_db", "patient") 
    def test_send_form_with_mismatched_code_returns_400_bad_request(
            self, client: TestClient, mismatched_otp_code_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=mismatched_otp_code_data,
            follow_redirects=False
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_form_input_err_msg_get_rendered_correctly(
            self, client: TestClient, mismatched_otp_code_data: dict[str, str]
    ) -> None:
        response = client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=mismatched_otp_code_data,
            follow_redirects=False
        )
        get_logger().debug(response.text)
        assert "Verification code does not match" in response.text

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_auth_succeed(
            self, client: TestClient, otp_code_data: dict[str, str]
    ) -> None:
        client.post(
            client.app.url_path_for("VerifyCode.form"),
            data=otp_code_data,
        )
        assert client.cookies.get("access_token")
        assert client.cookies.get("refresh_token")

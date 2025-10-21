from typing import override

import pytest
from bs4 import BeautifulSoup
from fastapi import status

from logger.setup import get_logger
from model.form_models import PhoneForm, OTPCodeForm
from data.auth_data import OTPCodeRedis
from tests.test_integration.web.conftest import (EndpointWithForm)


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
class TestLoginEndpoint(EndpointWithForm):
    base_url = "Login.form"

    @override
    def test_redirects(self, phone_data: dict[str, str]) -> None:
        super().test_redirects(phone_data, "VerifyCode.form")

    @override
    def test_invalid_form_data_returns_422(
            self, invalid_phone_data: dict[str, str]
    ) -> None:
        super().test_invalid_form_data_returns_422(invalid_phone_data)

    @override
    def test_validation_err_msgs_are_rendered_correctly(
            self, invalid_phone_data: dict[str, str]
    ) -> None:
        super().test_validation_err_msgs_are_rendered_correctly(
            PhoneForm, invalid_phone_data
        )

    def test_otp_code_is_created(
            self, phone_data: dict[str, str], otp_redis: OTPCodeRedis
    ) -> None:
        response = self.client.post(
            self._get_url(), data=phone_data, follow_redirects=False
        )
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert otp_redis.get(phone_data.get("phone"))


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("patients_data")
class TestVerifyCodeEndpoint(EndpointWithForm):
    base_url = "VerifyCode.form"

    @override
    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_redirects(self, otp_code_data: dict[str, str]) -> None:
        super().test_redirects(otp_code_data, "PatientAppointment.all")

    @override
    def test_invalid_form_data_returns_422(
            self, invalid_otp_code_data: dict[str, str]
    ) -> None:
        super().test_invalid_form_data_returns_422(invalid_otp_code_data)

    @override
    def test_validation_err_msgs_are_rendered_correctly(
            self, invalid_otp_code_data: dict[str, str]
    ) -> None:
        super().test_validation_err_msgs_are_rendered_correctly(
            OTPCodeForm, invalid_otp_code_data
        )

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_send_form_with_mismatched_code_returns_400_bad_request(
            self, mismatched_otp_code_data: dict[str, str]
    ) -> None:
        response = self._post_req(mismatched_otp_code_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_form_input_err_msg_get_rendered_correctly(
            self, mismatched_otp_code_data: dict[str, str]
    ) -> None:
        response = self._post_req(mismatched_otp_code_data)
        assert "Verification code does not match" in response.text

    def test_phone_field_is_hidden(self) -> None:
        response = self.client.get(self._get_url())
        soup = BeautifulSoup(response.text, "html.parser")
        hidden_elem = soup.find_all("input", {"type": "hidden"})[0]
        assert hidden_elem.get("id") == "phone"

    @pytest.mark.usefixtures("otp_code_db", "patient")
    def test_auth_succeed(self, otp_code_data: dict[str, str]) -> None:
        self.client.post(self._get_url(), data=otp_code_data)
        assert self.client.cookies.get("access_token")
        assert self.client.cookies.get("refresh_token")

import pytest
from fastapi import Response
from sqlmodel import Session

from logger.setup import get_logger
from exceptions.exc import (
    FormInputError, OTPCodeHashDoesNotMatch
)
from utils import SetUpTest
from model.form_models import OTPCodeForm
from service.auth_services import AuthService, OTPCodeService
from data.auth_data import OTPCodeRedis
from tests.test_integration.conftest import MockRequest


@pytest.fixture
def invalid_form(otp_code_form: OTPCodeForm) -> OTPCodeForm:
    otp_code_form.code = "000000"
    return otp_code_form


@pytest.fixture
def auth_service(session: Session, mock_request: MockRequest) -> AuthService:
    return AuthService(session, mock_request)


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.usefixtures("otp_code_db", "patient")
class TestAuthService:
    @pytest.fixture(autouse=True)
    def _service(self, auth_service: AuthService) -> None:
        self.service = auth_service

    @pytest.fixture(autouse=True)
    def _form(self, otp_code_form: OTPCodeForm) -> None:
        self.form = otp_code_form

    @pytest.fixture(autouse=True)
    def _mock_response(self, mock_response: Response) -> None:
        self.mock_response = mock_response

    def test_auth_succeed_for_existing_patient(self) -> None:
        self.service.authenticate(self.form, self.mock_response)
        access_token, refresh_token = self.mock_response.headers.values()[1:]
        assert "access_token" in access_token
        assert "refresh_token" in refresh_token
        get_logger().debug(access_token)
        get_logger().debug(refresh_token)

    def test_auth_succeed_for_nonexistent_patient(
            self, setup_test: SetUpTest,
    ) -> None:
        self.service.authenticate(self.form, self.mock_response)
        access_token, refresh_token = self.mock_response.headers.values()[1:]
        assert "access_token" in access_token
        assert "refresh_token" in refresh_token
        setup_test.delete_patient(self.form.phone)


class TestOTPCodeService:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test_create_override_existing(
            self,
            otp_code_service: OTPCodeService,
            patients_data: dict[str, str],
            otp_redis: OTPCodeRedis,
    ) -> None:
        phone = patients_data.get("phone")
        otp_code_service.create(patients_data.get("phone"))
        prev = otp_redis.get(phone)
        otp_code_service.create(patients_data.get("phone"))
        new = otp_redis.get(phone)
        assert not prev.model_dump() == new.model_dump()

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("otp_code_db")
    def test_verify_succeed(
            self,
            otp_code_service: OTPCodeService,
            otp_code_form: OTPCodeForm,
    ) -> None:
        is_matched = otp_code_service.verify(otp_code_form)
        assert is_matched is True

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("otp_code_db")
    def test_verify_raises_form_input_error_if_hash_does_not_match(
            self, otp_code_service: OTPCodeService, invalid_form: OTPCodeForm
    ) -> None:
        with pytest.raises(FormInputError):
            otp_code_service.verify(invalid_form)

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("otp_code_db")
    def test__hash_matches(
            self, otp_code_service: OTPCodeService, otp_code_form: OTPCodeForm,
    ) -> None:
        match = otp_code_service._hash_matches(otp_code_form)
        assert match is True

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    @pytest.mark.usefixtures("otp_code_db")
    def test__hash_matches_raises_does_not_match_error(
            self,
            otp_code_service: OTPCodeService,
            invalid_form: OTPCodeForm,
    ) -> None:
        with pytest.raises(OTPCodeHashDoesNotMatch):
            otp_code_service._hash_matches(invalid_form)

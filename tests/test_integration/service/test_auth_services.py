import pytest

from exceptions.exc import (
    FormInputError, OTPCodeHashDoesNotMatch
)
from model.form_models import OTPCodeForm
from model.auth_models import OTPCode
from service.auth_services import OTPCodeService
from data.auth_data import OTPCodeRedis
from data.patient_data import PatientSQLModel


@pytest.fixture
def otp_code_db(
        otp_code_service: OTPCodeService,
        otp_code_form: OTPCodeForm,
        otp_redis: OTPCodeRedis
) -> OTPCode:
    otp_code_service._save_otp_code(**otp_code_form.model_dump())
    otp_code = otp_redis.get(otp_code_form.phone)
    yield otp_code
    otp_redis.delete(otp_code_form.phone)


@pytest.fixture
def invalid_form(otp_code_form: OTPCodeForm) -> OTPCodeForm:
    otp_code_form.code = "000000"
    return otp_code_form


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

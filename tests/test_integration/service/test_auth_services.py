import pytest

from utils import SetUpTest
from service.auth_services import OTPCodeService
from service.patient_services import PatientService
from data.patient_data import PatientSQLModel, PatientCRUD


class TestOTPCodeService:
    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test_create_otp_code_for_existing_patient(
            self, 
            otp_code_service: OTPCodeService, 
            setup_test: SetUpTest,
            patient: PatientSQLModel
    ) -> None:
        otp_code_service.create_otp_code()
        patient_id = PatientCRUD.uuid_to_str(patient.id)
        created_otp_code = setup_test.find_otp_code_by_patient_id(patient_id)
        assert created_otp_code

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test_create_otp_code_registries_patient_and_set_otp_code(
            self,
            otp_code_service: OTPCodeService,
            patient_service: PatientService,
            patient_crud: PatientCRUD,
            setup_test: SetUpTest
    ) -> None:
        assert not patient_service._check_patient_exsits(
            otp_code_service.form.phone
        )
        otp_code_service.create_otp_code()
        patient_db = patient_crud.get_by_phone(otp_code_service.form.phone)
        otp_code = setup_test.find_otp_code_by_patient_id(patient_db.id)
        assert otp_code
        setup_test.delete_patient(otp_code_service.form.phone)

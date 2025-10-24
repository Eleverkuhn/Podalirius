from collections.abc import Iterator
from random import randint

from typing import Generator

import pytest
from sqlmodel import Session

from model.form_models import OTPCodeForm
from model.auth_models import OTPCode
from model.patient_models import PatientCreate
from service.auth_services import JWTTokenService, OTPCodeService
from service.appointment_services import AppointmentJWTTokenService
from service.patient_services import PatientService
from data import sql_models
from data.base_data import BaseSQLModel
from data.auth_data import OTPCodeRedis
from data.patient_data import PatientSQLModel, PatientCRUD
from utils import SetUpTest

type CreatedTestEntry = Generator[BaseSQLModel, None, None]


@pytest.fixture
def setup_test(session: Session) -> SetUpTest:
    return SetUpTest(session)


@pytest.fixture
def patient_create(patients_data: dict) -> PatientCreate:
    return PatientCreate(**patients_data)


@pytest.fixture
def patient_service(session: Session) -> PatientService:
    return PatientService(session)


@pytest.fixture
def patient_crud(session: Session) -> PatientCRUD:
    return PatientCRUD(session)


@pytest.fixture
def patient(
        setup_test: SetUpTest, patient_sql_model: PatientSQLModel
) -> Iterator[PatientSQLModel]:
    created = setup_test.create_entry(patient_sql_model)
    yield created
    setup_test.tear_down(created)


@pytest.fixture
def appointment(
        appointments_data: dict,
        patient: PatientSQLModel,
        setup_test: SetUpTest
) -> Iterator[sql_models.Appointment]:
    appointment_model = sql_models.Appointment(
        **appointments_data, patient_id=patient.id
    )
    created = setup_test.create_entry(appointment_model)
    yield created
    setup_test.tear_down(created)


@pytest.fixture
def jwt_token_appointment(
        jwt_token_service: JWTTokenService, appointment: sql_models.Appointment
) -> str:
    return jwt_token_service.create(appointment.id)


@pytest.fixture
def appointment_token_service(session: Session) -> AppointmentJWTTokenService:
    return AppointmentJWTTokenService(session)


@pytest.fixture
def otp_redis(request: pytest.FixtureRequest) -> OTPCodeRedis:
    otp_r = OTPCodeRedis()
    if hasattr(request, "param"):
        otp_r.lifetime = request.param
    return otp_r


@pytest.fixture
def otp_random(otp_code_service: OTPCodeService) -> OTPCode:
    phone = str(randint(1000000000,  9999999999))
    salt, hashed_value = otp_code_service._hash_otp_code(
        otp_code_service._generate_code()
    )
    return OTPCode(
        phone=phone,
        salt=salt,
        code=hashed_value,
    )


@pytest.fixture
def otp_set_random(otp_redis: OTPCodeRedis, otp_random: OTPCode) -> OTPCode:
    otp_redis.set(otp_random)
    return otp_random


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
def patient_str_id(patient: PatientSQLModel) -> str:
    return PatientCRUD.uuid_to_str(patient.id)


@pytest.fixture
def access_token(
        patient_str_id: str, jwt_token_service: JWTTokenService
) -> str:
    return jwt_token_service.create(patient_str_id)


@pytest.fixture
def cookies(access_token: str) -> dict[str, str]:
    return {"access_token": access_token}

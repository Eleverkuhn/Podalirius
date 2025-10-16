from collections.abc import Iterator
from datetime import timedelta
from random import randint

from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.auth_models import OTPCode
from model.patient_models import PatientCreate
from service.auth_services import JWTTokenService, OTPCodeService
from service.appointment_services import AppointmentJWTTokenService
from service.patient_services import PatientService
from data import sql_models
from data.base_sql_models import BaseSQLModel
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
    return jwt_token_service.create_access_token(appointment.id)


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

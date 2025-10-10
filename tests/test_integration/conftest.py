from collections.abc import Iterator
from datetime import timedelta

from pathlib import Path
from typing import Generator

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from service.auth_services import JWTTokenService
from service.appointment_services import AppointmentJWTTokenService
from data import sql_models
from data.base_sql_models import BaseSQLModel
from data.patient_data import PatientSQLModel
from utils import SetUpTest, read_fixture

type CreatedTestEntry = Generator[BaseSQLModel, None, None]


@pytest.fixture
def setup_test(session: Session) -> SetUpTest:
    return SetUpTest(session)


@pytest.fixture
def patient_create(patients_data: dict) -> PatientCreate:
    return PatientCreate(**patients_data)


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

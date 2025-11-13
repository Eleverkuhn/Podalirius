from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from random import randint

from typing import Generator

import pytest
from sqlmodel import Session, Sequence

from utils import read_fixture
from main import app
from model.form_models import OTPCodeForm
from model.auth_models import OTPCode
from model.patient_models import PatientCreate
from model.appointment_models import AppointmentOuter, AppointmentDateTime
from service.auth_services import JWTTokenService, OTPCodeService
from service.appointment_services import AppointmentJWTTokenService
from service.patient_services import PatientService
from data.base_data import BaseSQLModel, BaseCRUD
from data.sql_models import (
    Appointment, Doctor, ServiceToAppointment, Specialty, Service
)
from data.auth_data import OTPCodeRedis
from data.patient_data import Patient, PatientCRUD
from utils import SetUpTest

type CreatedTestEntry = Generator[BaseSQLModel, None, None]

appointment_status = ["pending", "completed", "cancelled"]  # Is used for parametrizing 'filtered_appointments' fixture


class MockRequest:
    def __init__(self, cookies: dict[str, str] | dict = {}) -> None:
        self.app = app
        self.cookies = cookies


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
class BasePatientTest:
    pass


@pytest.mark.parametrize("doctor", [0], indirect=True)
class BaseDoctorTest:
    pass


@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
class BaseAppointmentTest:
    pass


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
        setup_test: SetUpTest, patient_sql_model: Patient
) -> Iterator[Patient]:
    created = setup_test.create_entry(patient_sql_model)
    yield created
    setup_test.tear_down(created)


@pytest.fixture
def appointments_data(
        fixture_dir: Path, request: pytest.FixtureRequest
) -> list[dict]:
    data = read_fixture(
        fixture_dir.joinpath("test_appointments.json")
    )
    return data.get(request.param)


@pytest.fixture
def get_appointment(
        appointments_data: list[dict], request: pytest.FixtureRequest
) -> dict:
    appointment = appointments_data[request.param]
    return appointment


@pytest.fixture
def appointment(
        get_appointment: dict,
        patient: Patient,
        setup_test: SetUpTest
) -> Iterator[Appointment]:
    appointment_model = Appointment(
        **get_appointment, patient_id=patient.id
    )
    created = setup_test.create_entry(appointment_model)
    yield created
    setup_test.tear_down(created)


@pytest.fixture
def appointments(
        patient: Patient, appointments_data: dict, setup_test: SetUpTest
) -> list[Appointment]:
    appointments = [
        Appointment(**appointment, patient_id=patient.id)
        for appointment
        in appointments_data
    ]
    setup_test.create_multiple(appointments)
    return appointments


@pytest.fixture
def converted_appointments(
        appointments: list[Appointment]
) -> list[AppointmentOuter]:
    patient_crud = PatientCRUD(None, None, None)
    converted_appointments = patient_crud._convert_appointments(appointments)
    return converted_appointments


@pytest.fixture
def filtered_appointments(
        converted_appointments: list[AppointmentOuter],
        request: pytest.FixtureRequest
) -> tuple[str, list[AppointmentOuter]]:
    status = request.param
    pending_appointments = [
        appointment
        for appointment
        in converted_appointments
        if appointment.status == request.param
    ]
    return (status, pending_appointments)


@pytest.fixture
def link_services_to_appointments(
        appointments: list[Appointment], setup_test: SetUpTest
) -> None:
    services_to_appointments = [
        ServiceToAppointment(service_id=1, appointment_id=appointment.id)
        for appointment
        in appointments
    ]
    setup_test.create_multiple(services_to_appointments)


@pytest.fixture
def jwt_token_appointment(
        jwt_token_service: JWTTokenService, appointment: Appointment
) -> str:
    token = jwt_token_service.create(appointment.id)
    return token


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
def patient_str_id(patient: Patient) -> str:
    return PatientCRUD.uuid_to_str(patient.id)


@pytest.fixture
def access_token(
        patient_str_id: str, jwt_token_service: JWTTokenService
) -> str:
    token = jwt_token_service.create(patient_str_id)
    return token


@pytest.fixture
def cookies(access_token: str) -> dict[str, str]:
    return {"access_token": access_token}


@pytest.fixture
def doctors(session: Session) -> Sequence[Doctor]:
    return BaseCRUD(session, Doctor, Doctor).get_all()


@pytest.fixture
def doctor(
        doctors: Sequence[Doctor], request: pytest.FixtureRequest
) -> Doctor:
    return doctors[request.param]


@pytest.fixture
def reschedule_appointment_form() -> AppointmentDateTime:
    current = datetime.now().replace(microsecond=0)
    current_date, current_time = current.date(), current.time()
    form = AppointmentDateTime(date=current_date, time=current_time)
    return form


@pytest.fixture
def patient_update_info(patient: Patient) -> PatientCreate:
    update_data = {"phone": "8888888888", "last_name": "updated"}
    update_info = PatientCreate(
        first_name=patient.first_name,
        middle_name=patient.middle_name,
        birth_date=patient.birth_date,
        **update_data
    )
    return update_info


@pytest.fixture
def mock_request(cookies: dict[str, str]) -> MockRequest:
    mock_request = MockRequest(cookies)
    return mock_request


@pytest.fixture
def mock_request_with_no_cookies() -> MockRequest:
    mock_request = MockRequest()
    return mock_request


@pytest.fixture
def specialties(session: Session) -> Sequence[Specialty]:
    specialties_crud = BaseCRUD(session, Specialty, Specialty)
    specialties = specialties_crud.get_all()
    return specialties


@pytest.fixture
def specialty(
        specialties: Sequence[Specialty], request: pytest.FixtureRequest
) -> Specialty:
    specialty = specialties[request.param]
    return specialty


@pytest.fixture
def all_services(session: Session) -> Sequence[Service]:
    crud = BaseCRUD(session, Service, Service)
    services = crud.get_all()
    return services


@pytest.fixture
def lab_tests(all_services: Sequence[Service]) -> list[Service]:
    lab_tests = [
        service
        for service
        in all_services
        if service.type.id == 3
    ]
    return lab_tests

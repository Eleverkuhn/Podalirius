from decimal import Decimal

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from utils import SetUpTest
from model.appointment_models import AppointmentOuter
from service.service_services import ServiceDataConstructor
from data.base_data import BaseCRUD
from data.sql_models import Appointment, Service, ServiceToAppointment
from data.appointment_data import AppointmentDataConverter


@pytest.fixture
def service_id() -> int:
    return 1


@pytest.fixture
def link_service_to_appointment(
        service_id: int, appointment: Appointment, setup_test: SetUpTest
) -> None:
    entry = ServiceToAppointment(
        service_id=service_id, appointment_id=appointment.id
    )
    setup_test.create_entry(entry)


@pytest.fixture
def converter(appointment: Appointment) -> AppointmentDataConverter:
    converter = AppointmentDataConverter(appointment)
    return converter


@pytest.fixture
def service(session: Session, service_id: int) -> Service:
    crud = BaseCRUD(session, Service, Service)
    service = crud._get(service_id)
    return service


@pytest.fixture
def calculate_price_expected_output(
        appointment: Appointment, service: Service
) -> Decimal:
    constructor = ServiceDataConstructor()
    price = constructor._calculate_price(appointment.doctor_id, service)
    return price


@pytest.fixture
def get_services_expected_output(service: Service) -> list[Service]:
    return [service]


@pytest.fixture
def to_outer_expected_output(
        appointment: Appointment, calculate_price_expected_output: Decimal
) -> AppointmentOuter:
    outer = AppointmentOuter(
        **appointment.model_dump(),
        doctor=appointment.doctor.full_name,
        price=calculate_price_expected_output
    )
    return outer


@pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize("appointments_data", ["patient_1"], indirect=True)
@pytest.mark.parametrize("get_appointment", [0], indirect=True)
@pytest.mark.usefixtures("link_service_to_appointment")
class TestAppointmentDataConverter:
    @pytest.fixture(autouse=True)
    def _converter(self, converter: AppointmentDataConverter) -> None:
        self.converter = converter

    def test_to_otuer(
            self, to_outer_expected_output: AppointmentOuter
    ) -> None:
        outer = self.converter.to_outer()
        assert outer == to_outer_expected_output

    def test__calculate_appointment_price(
            self, calculate_price_expected_output: Decimal
    ) -> None:
        price = self.converter._calculate_appointment_price()
        assert price == calculate_price_expected_output

    def test__get_serivces(
            self, get_services_expected_output: list[Service]
    ) -> None:
        services = self.converter._get_services()
        assert services == get_services_expected_output
        get_logger().debug(services)

from pathlib import Path

import pytest
from sqlmodel import Session

from logger.setup import get_logger
from utils import read_fixture
from service.service_services import ServiceDataConstructor
from data.sql_models import Doctor


@pytest.fixture
def fixture_dir() -> Path:
    return Path("src", "data", "sql", "fixtures")


@pytest.fixture
def doctors_to_services_data(
        fixture_dir: Path, request: pytest.FixtureRequest
) -> dict[str, str]:
    content = read_fixture(fixture_dir.joinpath("doctors_to_services.json"))
    return content[request.param]


@pytest.fixture
def service(session: Session) -> ServiceDataConstructor:
    return ServiceDataConstructor(session)


class TestServiceDataConstructor:
    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__traverese(
            self, doctor: Doctor, service: ServiceDataConstructor
    ) -> None:
        traversed = service._traverse(doctor.id, doctor.services)
        assert traversed
        get_logger().debug(traversed)

    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__calculate_price(
            self, doctor: Doctor, service: ServiceDataConstructor
    ) -> None:
        price = service._calculate_price(doctor.id, doctor.services[0])
        expected_price = 3000
        assert price == expected_price

    @pytest.mark.parametrize("doctors_to_services_data", [0], indirect=True)
    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__get_doctor_to_service_markup(
            self,
            doctor: Doctor,
            service: ServiceDataConstructor,
            doctors_to_services_data: dict[str, str]
    ) -> None:
        markup = service._get_doctor_to_service_markup(
            doctor.id, doctor.services[0]
        )
        assert markup == doctors_to_services_data.get("markup")

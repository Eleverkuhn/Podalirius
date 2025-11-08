from pathlib import Path

import pytest

from utils import read_fixture
from service.service_services import ServiceDataConstructor, PriceCalculator
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


@pytest.mark.parametrize("doctor", [0], indirect=True)
class BaseServiceTest:
    @pytest.fixture(autouse=True)
    def _doctor(self, doctor: Doctor) -> None:
        self.doctor = doctor


class TestServiceDataConstructor(BaseServiceTest):

    @pytest.fixture(autouse=True)
    def _constructor(self, doctor: Doctor) -> None:
        self.constructor = ServiceDataConstructor(doctor)

    def test_exec(self) -> None:
        dumped_services = self.constructor.exec()
        assert dumped_services


class TestPriceCalculator(BaseServiceTest):
    @pytest.fixture(autouse=True)
    def _calculator(self, doctor: Doctor) -> None:
        self.calculator = PriceCalculator(doctor, doctor.services[0])

    def test__calculate_price(self) -> None:
        price = self.calculator.exec()
        expected_price = 3000
        assert price == expected_price

    @pytest.mark.parametrize("doctors_to_services_data", [0], indirect=True)
    def test__get_doctor_to_service_markup(
            self, doctors_to_services_data: dict[str, str]
    ) -> None:
        markup = self.calculator._get_doctor_to_service_markup()
        assert markup == doctors_to_services_data.get("markup")

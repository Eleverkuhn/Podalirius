from pathlib import Path

import pytest
from sqlmodel import Session

from utils import read_fixture
from service.service_services import (
    ServiceDataConstructor, PriceCalculator, ServicePage
)
from data.sql_models import Doctor, Service


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
def service_page(session: Session) -> ServicePage:
    service_page = ServicePage(session)
    return service_page


class TestServicePage:
    def test_get_lab_tests(
            self, lab_tests: list[Service], service_page: ServicePage
    ) -> None:
        lab_tests = sorted(lab_tests, key=lambda s: s.price)
        lab_tests_db = service_page.get_lab_tests()
        for lab_test_db, lab_test in zip(lab_tests_db, lab_tests):
            assert lab_test_db.title == lab_test.title
            assert lab_test_db.price == int(lab_test.price)


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

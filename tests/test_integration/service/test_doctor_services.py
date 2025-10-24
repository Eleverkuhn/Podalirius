from pathlib import Path

import pytest
from sqlmodel import Sequence

from logger.setup import get_logger
from utils import read_fixture
from service.doctor_services import DoctorDataConstructor
from data.sql_models import Doctor


@pytest.fixture
def fixture_dir() -> Path:
    return Path("src", "data", "sql", "fixtures")


@pytest.fixture
def doctors_data(
        fixture_dir: Path, request: pytest.FixtureRequest
) -> dict[str, str]:
    doctors = read_fixture(fixture_dir.joinpath("doctors.json"))
    return doctors[request.param]


class TestDoctorDataConstructor:
    def test__traveerse(
            self,
            doctor_service: DoctorDataConstructor,
            doctors: Sequence[Doctor]
    ) -> None:
        result = doctor_service._traverse(doctors)
        assert result
        get_logger().debug(result)

    @pytest.mark.parametrize("doctors_data", [0], indirect=True)
    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__dump(
            self,
            doctor_service: DoctorDataConstructor,
            doctor: Doctor,
            doctors_data: dict[str, str]
    ) -> None:
        dumped = doctor_service._dump(doctor)
        expected_full_name = (
            f"{doctors_data.get('first_name')} "
            f"{doctors_data.get('middle_name')} "
            f"{doctors_data.get('last_name')}"
        )
        assert dumped.get("full_name") == expected_full_name

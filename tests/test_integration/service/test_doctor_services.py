from datetime import time
from pathlib import Path

import pytest
from sqlmodel import Sequence

from logger.setup import get_logger
from utils import read_fixture
from service.doctor_services import (
    DoctorDataConstructor, WorkScheduleDataConstructor
)
from data.sql_models import Doctor, WorkSchedule


@pytest.fixture
def fixture_dir() -> Path:
    return Path("src", "data", "sql", "fixtures")


@pytest.fixture
def doctors_data(
        fixture_dir: Path, request: pytest.FixtureRequest
) -> dict[str, str]:
    doctors = read_fixture(fixture_dir.joinpath("doctors.json"))
    return doctors[request.param]


@pytest.fixture
def work_schedules_data(fixture_dir: Path) -> list[dict] | dict:
    work_schedules = read_fixture(fixture_dir.joinpath("work_schedules.json"))
    return work_schedules


@pytest.fixture
def mock_work_schedule() -> WorkSchedule:
    work_day = WorkSchedule(
            doctor_id=1,
            weekday="1",
            start_time=time(hour=8),
            end_time=time(hour=16)
        )
    return work_day


class TestDoctorDataConstructor:
    def test__traveerse(
            self,
            doctor_service: DoctorDataConstructor,
            doctors: Sequence[Doctor]
    ) -> None:
        result = doctor_service._traverse(doctors)
        assert result
        get_logger().debug(result)

    @pytest.mark.parametrize("doctors_data", [1], indirect=True)
    @pytest.mark.parametrize("doctor", [1], indirect=True)
    def test__dump(
            self,
            doctor_service: DoctorDataConstructor,
            doctor: Doctor,
            doctors_data: dict[str, str]
    ) -> None:  # FIX: change this test
        dumped = doctor_service._dump(doctor)
        expected_full_name = (
            f"{doctors_data.get('first_name')} "
            f"{doctors_data.get('middle_name')} "
            f"{doctors_data.get('last_name')}"
        )
        assert dumped.get("full_name") == expected_full_name

    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__get_schedule(
        self, doctor_service: DoctorDataConstructor, doctor: Doctor
    ) -> None:
        schedule = doctor_service._get_schedule(doctor)
        get_logger().debug(schedule)

    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test__get_appointments(
            self, doctor_service: DoctorDataConstructor, doctor: Doctor
    ) -> None:
        appointments = doctor_service._get_appointments(doctor)
        get_logger().debug(doctor)
        get_logger().debug(doctor.appointments)
        assert appointments
        assert len(appointments) == 3


class TestWorkScheduleService:
    def test_exec(self, mock_work_schedule: WorkSchedule) -> None:
        constructor = WorkScheduleDataConstructor(mock_work_schedule)
        schedule = constructor.exec()
        assert schedule
        get_logger().debug(schedule)

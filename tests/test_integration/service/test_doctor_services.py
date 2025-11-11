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
from tests.test_integration.conftest import BaseDoctorTest


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
    @pytest.fixture(autouse=True)
    def _constructor(
            self, doctor_data_constructor: DoctorDataConstructor
    ) -> None:
        self.constructor = doctor_data_constructor

    def test_exec(self) -> None:
        result = self.constructor.exec()
        assert result
        get_logger().debug(result)

    @pytest.mark.parametrize("doctor", [1], indirect=True)
    def test__dump(self, doctor: Doctor) -> None:
        dumped = self.constructor._dump(doctor)
        assert dumped


class TestDoctorDataConstructorSingle(BaseDoctorTest):
    @pytest.fixture(autouse=True)
    def _constructor(
            self, doctor_data_constructor_single: DoctorDataConstructor
    ) -> None:
        self.constructor = doctor_data_constructor_single

    def test__get_schedule(self, doctor: Doctor) -> None:
        self.constructor.doctor = doctor
        schedule = self.constructor._get_schedule()
        assert schedule

    def test__get_appointments(self, doctor: Doctor) -> None:
        self.constructor.doctor = doctor
        appointments = self.constructor._get_appointments()
        assert appointments
        assert len(appointments) == 3


class TestWorkScheduleService:
    def test_exec(self, mock_work_schedule: WorkSchedule) -> None:
        constructor = WorkScheduleDataConstructor(mock_work_schedule)
        schedule = constructor.exec()
        assert schedule

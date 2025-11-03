from datetime import date, time, datetime, timedelta

import pytest

from logger.setup import get_logger
from service.appointment_services import (
    AppointmentSchedule,
    AppointmentShceduleDataConstructor,
)


@pytest.fixture
def today() -> date:
    return date.today()


@pytest.fixture
def week(today: date) -> list[date]:
    return [today + timedelta(days=day) for day in range(7)]


@pytest.fixture
def booked_hours() -> list[str]:
    return ["08:00:00", "08:30:00"]


@pytest.fixture
def free_hours() -> str:
    return "09:00:00"


@pytest.fixture
def booked_appointment_times(
        week: list[date], booked_hours: list[str]
) -> list[datetime]:
    data = [
        datetime.combine(day, time.fromisoformat(booked_time))
        for day in week
        for booked_time in booked_hours
    ]
    return data


@pytest.fixture
def expected_grouped_booked_dates(
        week: list[date], booked_hours: list[time]
) -> AppointmentSchedule:
    data = {
        day: {booked_hours[0], booked_hours[1]}
        for day
        in week
    }
    return data


@pytest.fixture
def doctor_schedule(
        booked_hours: list[time], free_hours: time
) -> dict[int, list[datetime]]:
    data = {
        weekday: {booked_hours[0], booked_hours[1], free_hours}
        for weekday
        in range(7)
    }
    return data


@pytest.fixture
def expected_appointment_schedule(
        week: list[date], free_hours: time
) -> AppointmentSchedule:
    """Expected data for AppointmentShceduleDataConstructor.exec()"""
    data = {day.isoformat(): [free_hours] for day in week}
    return data


@pytest.fixture
def constructor(
        doctor_schedule: dict[int, list[datetime]],
        booked_appointment_times: list[datetime],
        request: pytest.FixtureRequest
) -> AppointmentShceduleDataConstructor:
    if hasattr(request, "param"):
        constructor = AppointmentShceduleDataConstructor(
            doctor_schedule, booked_appointment_times, request.param
        )
    else:
        constructor = AppointmentShceduleDataConstructor(
            doctor_schedule, booked_appointment_times
        )
    return constructor


@pytest.fixture
def constructor_blank() -> AppointmentShceduleDataConstructor:
    return AppointmentShceduleDataConstructor({}, [])


class TestAppointmentScheduleDataConstructor:
    @pytest.mark.parametrize("constructor", [timedelta(days=7)], indirect=True)
    def test_exec(
            self,
            constructor: AppointmentShceduleDataConstructor,
            expected_appointment_schedule: AppointmentSchedule
    ) -> None:
        appointment_schedule = constructor.exec()
        assert appointment_schedule == expected_appointment_schedule

    def test__group_by_date(
            self,
            constructor_blank: AppointmentShceduleDataConstructor,
            booked_appointment_times: list[datetime],
            expected_grouped_booked_dates: AppointmentSchedule
    ) -> None:
        grouped_booked_dates = constructor_blank._group_by_date(
            booked_appointment_times
        )
        assert grouped_booked_dates == expected_grouped_booked_dates

    def test__set_free_hours(
            self,
            constructor: AppointmentShceduleDataConstructor,
            doctor_schedule: dict[int, list[datetime]],
    ) -> None:
        constructor.free_hours = doctor_schedule.get(0)
        constructor._set_free_appointment_times()
        assert constructor.schedule
        get_logger().debug(constructor.schedule)

    def test__day_is_fully_booked(
            self,
            constructor_blank: AppointmentShceduleDataConstructor
    ) -> None:
        set_1 = {'a', 'b', 'c'}
        set_2 = {'a', 'b', 'c'}
        set_diff = set_1 - set_2
        constructor_blank.free_hours = set_diff
        constructor_blank._set_free_appointment_times()
        assert not constructor_blank.schedule
        get_logger().debug(constructor_blank.schedule)

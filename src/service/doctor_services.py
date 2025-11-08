from datetime import datetime, date, time, timedelta

from service.appointment_services import AppointmentShceduleDataConstructor
from service.service_services import ServiceDataConstructor
from data.sql_models import Doctor, WorkSchedule


class DoctorDataConstructor:
    def __init__(self, doctors: list[Doctor]) -> None:
        self.doctors = doctors

    def exec(self) -> list[dict]:
        dumped_doctors = [self._dump(doctor) for doctor in self.doctors]
        return dumped_doctors

    def _dump(self, doctor: Doctor) -> dict:
        self._set_doctors_data(doctor)
        self._add_fields_to_dumped_doctor()
        return self.dumped_doctor

    def _set_doctors_data(self, doctor: Doctor) -> None:
        self.doctor = doctor
        self.dumped_doctor = {"id": self.doctor.id}

    def _add_fields_to_dumped_doctor(self) -> None:
        self._add_full_name()
        self._add_services()
        self._add_appointment_schedule()

    def _add_full_name(self) -> None:
        self.dumped_doctor.update({"full_name": self.doctor.full_name})

    def _add_services(self) -> None:
        constructor = ServiceDataConstructor(self.doctor)
        services = constructor.exec()
        self.dumped_doctor.update({"services": services})

    def _add_appointment_schedule(self) -> None:
        # TODO: fix this import

        doctor_schedule = self._get_schedule()
        appointments = self._get_appointments()
        constructor = AppointmentShceduleDataConstructor(
            doctor_schedule, appointments
        )
        appointment_schedule = constructor.exec()
        self.dumped_doctor.update({"schedule": appointment_schedule})

    def _get_schedule(self) -> dict:
        schedule = {}
        for work_day in self.doctor.work_days:
            self._populate_schedule(work_day, schedule)
        return schedule

    def _populate_schedule(
            self, work_day: WorkSchedule, schedule: dict
    ) -> None:
        schedule_value = self._get_schedule_value(work_day)
        schedule.update(schedule_value)

    def _get_schedule_value(self, work_day: WorkSchedule) -> dict:
        week_day, constructor = self._construct_schedule_value_data(work_day)
        schedule_value = {week_day: constructor.exec()}
        return schedule_value

    def _construct_schedule_value_data(
            self, work_day: WorkSchedule
    ) -> tuple[int, "WorkScheduleDataConstructor"]:
        week_day = self._get_week_day(work_day)
        constructor = WorkScheduleDataConstructor(work_day)
        return week_day, constructor

    def _get_week_day(self, work_day: WorkSchedule) -> int:
        week_day_int = int(work_day.weekday)
        return week_day_int

    def _get_appointments(self) -> set[tuple[date, time]]:
        appointments = set(
            (appointment.date, appointment.time)
            for appointment
            in self.doctor.appointments
            if appointment.status == "pending"
        )
        return appointments


class WorkScheduleDataConstructor:
    appointment_duration = timedelta(minutes=30)

    def __init__(self, work_day: WorkSchedule) -> None:
        self.work_day = work_day
        self.appointment_time = self._set_appointment_time()
        self.schedule = set()

    def _set_appointment_time(self) -> datetime:
        return datetime.combine(date.today(), self.work_day.start_time)

    def exec(self) -> set[time]:
        self._create_schedule()
        return self.schedule

    def _create_schedule(self) -> set[time]:
        while self.appointment_time.time() < self.work_day.end_time:
            self._add_appointment_time()
        return self.schedule

    def _add_appointment_time(self) -> None:
        self.schedule.add(self.appointment_time.time().isoformat())
        self.appointment_time += self.appointment_duration

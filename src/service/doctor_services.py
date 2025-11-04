from datetime import datetime, date, time, timedelta

from logger.setup import get_logger
from service.base_services import BaseService
from service.service_services import ServiceDataConstructor
from data.sql_models import Doctor, Service, WorkSchedule, Appointment


class DoctorDataConstructor(BaseService):
    def _traverse(self, doctors: list[Doctor]) -> list[dict]:
        return [self._dump(doctor) for doctor in doctors]

    def _dump(self, doctor: Doctor) -> dict:
        dumped = {"id": doctor.id}
        self._add_full_name(dumped, doctor)
        self._add_services(dumped, doctor.services)
        self._add_appointment_schedule(dumped, doctor)
        return dumped

    def _add_full_name(
            self, dumped_doctor: dict[str, str], doctor: Doctor
    ) -> None:
        full = f"{doctor.first_name} {doctor.middle_name} {doctor.last_name}"
        dumped_doctor.update({"full_name": full})

    def _add_services(
            self, dumped_doctor: dict[str, str], services: list[Service]
    ) -> dict:
        services = ServiceDataConstructor(self.session)._traverse(
            dumped_doctor.get("id"), services
        )
        dumped_doctor.update({"services": services})
        return dumped_doctor

    def _add_appointment_schedule(
            self, dumped_doctor: dict[str, str], doctor: Doctor
    ) -> None:
        # TODO: fix this import
        from service.appointment_services import AppointmentShceduleDataConstructor

        doctor_schedule = self._get_schedule(doctor)
        appointment_schedule = AppointmentShceduleDataConstructor(
            doctor_schedule, self._get_appointments(doctor)
        ).exec()
        dumped_doctor.update({"schedule": appointment_schedule})

    def _get_schedule(self, doctor: Doctor) -> dict:
        schedule = {
            int(work_day.weekday): WorkScheduleDataConstructor(work_day).exec()
            for work_day
            in doctor.work_days
        }
        return schedule

    def _get_appointments(self, doctor: Doctor) -> set[tuple[date, time]]:
        appointments = set(
            (appointment.date, appointment.time)
            for appointment
            in doctor.appointments
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

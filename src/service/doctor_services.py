from service.base_services import BaseService
from service.service_services import ServiceDataConstructor
from data.sql_models import Doctor, Service


class DoctorDataConstructor(BaseService):
    def _traverse(self, doctors: list[Doctor]) -> list[dict]:
        return [self._dump(doctor) for doctor in doctors]

    def _dump(self, doctor: Doctor) -> dict[str, str | int]:
        dumped = {
            "id": doctor.id,
            "full_name": (
                f"{doctor.first_name} "
                f"{doctor.middle_name} "
                f"{doctor.last_name}"
            )
        }
        dumped_doctor_with_services = self._add_services(dumped, doctor.services)
        return dumped_doctor_with_services

    def _add_services(
            self, dumped_doctor: dict[str, str], services: list[Service]
    ) -> dict:
        services = ServiceDataConstructor(self.session)._traverse(
            dumped_doctor.get("id"), services
        )
        dumped_doctor.update({"services": services})
        return dumped_doctor

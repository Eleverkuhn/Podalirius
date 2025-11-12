from decimal import Decimal

from model.doctor_models import DoctorOuter
from service.service_services import PriceCalculator
from data.sql_models import Doctor, Service


class DoctorDataConverter:
    def __init__(self, doctors: list[Doctor]) -> None:
        self.doctors = doctors

    def convert_multiple_doctors_to_outer(self) -> list:
        doctors_outer = [
            self.convert_doctor_to_outer(doctor)
            for doctor
            in self.doctors
        ]
        return doctors_outer

    def convert_doctor_to_outer(self, doctor: Doctor) -> DoctorOuter:
        consultations = self._get_consultations(doctor)
        dumped_doctor = doctor.model_dump()
        doctor_outer = DoctorOuter(
            **dumped_doctor,
            consultations=consultations,
            full_name=doctor.full_name,
            experience_in_years=doctor.experience_in_years
        )
        return doctor_outer

    def _get_consultations(self, doctor: Doctor) -> list[dict[str, int]]:
        consultations = [
            self._construct_consultation_info(doctor, service)
            for service
            in doctor.services
            if service.type.id == 1
        ]
        return consultations

    def _construct_consultation_info(
            self, doctor: Doctor, service: Service
    ) -> dict[str | int]:
        price = self._get_service_price(doctor, service)
        consultation_info = {service.title: price}
        return consultation_info

    def _get_service_price(self, doctor: Doctor, service: Service) -> int:
        price = PriceCalculator(doctor, service).exec()
        converted_price = self._convert_price_to_int(price)
        return converted_price

    def _convert_price_to_int(self, price: Decimal) -> int:
        converted_price = int(price)
        return converted_price

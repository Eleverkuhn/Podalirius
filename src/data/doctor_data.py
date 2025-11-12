from decimal import Decimal
from typing import override

from sqlmodel import Session

from model.doctor_models import DoctorOuter, DoctorDetail
from model.service_models import ServiceOuter
from service.service_services import PriceCalculator
from data.sql_models import Doctor, Service
from data.base_data import BaseCRUD
from data.service_data import ServiceDataConverter


class DoctorCRUD(BaseCRUD):
    def __init__(
            self,
            session: Session,
            sql_model: type[Doctor] = Doctor,
            return_model: type[DoctorDetail] = DoctorDetail
    ) -> None:
        super().__init__(session, sql_model, return_model)

    @override
    def get(self, id: int) -> DoctorDetail:
        doctor = self._get(id)
        doctor_detail = DoctorDataConverter(doctor=doctor).convert_to_detail()
        return doctor_detail


class DoctorDataConverter:
    def __init__(
            self,
            doctors: list[Doctor] | None = None,
            doctor: Doctor | None = None
    ) -> None:
        self.doctors = doctors
        self.doctor = doctor

    def convert_to_detail(self) -> DoctorDetail:
        dumped_doctor = self.doctor.model_dump()
        doctor_detail = DoctorDetail(
            **dumped_doctor,
            full_name=self.doctor.full_name,
            experience_in_years=self.doctor.experience_in_years,
            services=self._get_converted_services()
        )
        return doctor_detail

    def _get_converted_services(self) -> list[ServiceOuter]:
        services_outer = [
            ServiceDataConverter(self.doctor, service).convert_to_outer()
            for service
            in self.doctor.services
        ]
        return services_outer

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

from decimal import Decimal

from sqlmodel import Sequence

from data.sql_models import Doctor, Service


class ServiceDataConstructor:
    def __init__(self, doctor: Doctor) -> None:
        self.doctor = doctor
        self.doctor_id: int = doctor.id
        self.services: Sequence[Doctor] = doctor.services

    def exec(self) -> list[dict]:
        dumped_services = [
            self._dump(service) for service in self.services
        ]
        return dumped_services

    def _dump(self, service: Service) -> dict:
        self._set_service_data(service)
        self._add_price()
        return self.dumped_service

    def _set_service_data(self, service) -> None:
        self.service = service
        self.dumped_service = self.service.model_dump(include=["id", "title"])

    def _add_price(self) -> None:
        price_calculator = PriceCalculator(self.doctor, self.service)
        price = price_calculator.exec()
        self.dumped_service.update({"price": str(price)})


class PriceCalculator:
    def __init__(self, doctor: Doctor, service: Service) -> None:
        self.doctor = doctor
        self.service = service

    def exec(self) -> Decimal:
        doctor_markup = self._get_doctor_to_service_markup()
        price = self.service.type.price + self.service.markup + doctor_markup
        return price

    def _get_doctor_to_service_markup(self) -> Decimal:
        for link in self.service.service_links:
            if (link.doctor_id == self.doctor.id) and \
                    (link.service_id == self.service.id):
                return link.markup

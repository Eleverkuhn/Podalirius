from decimal import Decimal

from service.base_services import BaseService
from data.sql_models import Service


class ServiceDataConstructor:
    def _traverse(self, doctor_id: int, services: list[Service]) -> list[dict]:
        return [self._dump(doctor_id, service) for service in services]

    def _dump(self, doctor_id: int, service: Service) -> dict:
        dumped = service.model_dump(include=["id", "title"])
        self._add_price(doctor_id, service, dumped)
        return dumped

    def _add_price(
            self,
            doctor_id: int,
            service: Service,
            dumped_service: dict[str, str],
    ) -> dict:
        price = self._calculate_price(doctor_id, service)
        dumped_service.update({"price": str(price)})
        return dumped_service

    def _calculate_price(self, doctor_id: int, service: Service) -> Decimal:
        doctor_markup = self._get_doctor_to_service_markup(doctor_id, service)
        price = service.type.price + service.markup + doctor_markup
        return price

    def _get_doctor_to_service_markup(
            self, doctor_id: int, service: Service
    ) -> Decimal:
        for link in service.service_links:
            if link.doctor_id == doctor_id and link.service_id == service.id:
                return link.markup

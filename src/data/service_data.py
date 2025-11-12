from decimal import Decimal

from model.service_models import ServiceOuter
from service.service_services import PriceCalculator
from data.sql_models import Service, Doctor


class ServiceDataConverter:
    def __init__(self, doctor: Doctor, service: Service) -> None:
        self.service = service
        self.doctor = doctor

    def convert_to_outer(self) -> ServiceOuter:
        service_outer = ServiceOuter(
            title=self.service.title,
            price=self._get_price()
        )
        return service_outer

    def _get_price(self) -> int:
        price = PriceCalculator(self.doctor, self.service).exec()
        converted_price = self._convert_price_to_int(price)
        return converted_price

    def _convert_price_to_int(self, price: Decimal) -> int:
        converted_price = int(price)
        return converted_price

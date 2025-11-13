from decimal import Decimal

from sqlmodel import Session

from model.service_models import ServiceOuter
from data.base_data import BaseCRUD
from data.sql_models import Service, Doctor


class ServiceCRUD(BaseCRUD):
    def __init__(
        self,
        session: Session,
        sql_model: type[Service] = Service,
        return_model: type[ServiceOuter] = ServiceOuter
    ) -> None:
        super().__init__(session, sql_model, return_model)

    def get_lab_tests(self) -> list[ServiceOuter]:
        all_services = self.get_all()
        lab_tests = [
            ServiceOuter(title=service.title, price=service.price)
            for service
            in all_services
            if service.type.id == 3
        ]
        return lab_tests


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


class PriceCalculator:
    def __init__(self, doctor: Doctor, service: Service) -> None:
        self.doctor = doctor
        self.service = service

    def exec(self) -> Decimal:
        doctor_markup = self._get_doctor_to_service_markup()
        price = self.service.price + doctor_markup
        return price

    def _get_doctor_to_service_markup(self) -> Decimal:
        for link in self.service.service_links:
            if (link.doctor_id == self.doctor.id) and \
                    (link.service_id == self.service.id):
                return link.markup

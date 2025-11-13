from fastapi import Depends
from sqlmodel import Sequence, Session

from data.connections import MySQLConnection
from data.sql_models import Doctor, Service
from data.service_data import ServiceCRUD, PriceCalculator


class ServicePage:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.crud = ServiceCRUD(session)

    def get_lab_tests(self) -> list[Service]:
        lab_tests = self.crud.get_lab_tests()
        sorted_lab_tests = self._sort_by_price(lab_tests)
        return sorted_lab_tests

    def _sort_by_price(self, lab_tests: list[Service]) -> list[Service]:
        sorted_lab_tests = sorted(lab_tests, key=lambda s: s.price)
        return sorted_lab_tests


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


def get_service_page(
        session: Session = Depends(MySQLConnection.get_session)
) -> ServicePage:
    service_page = ServicePage(session)
    return service_page

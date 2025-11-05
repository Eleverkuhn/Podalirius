from decimal import Decimal
from typing import Callable

from model.appointment_models import AppointmentOuter
from service.service_services import ServiceDataConstructor
from data.sql_models import Appointment, Service


class AppointmentDataConverter:
    """
    A set of utilites for conversion sqlmodel 'Appointment' to appointment
    pydantic models
    """
    def __init__(self, appointment: Appointment) -> None:
        self.appointment = appointment
        self.service_constructor = ServiceDataConstructor()

    def to_outer(self) -> AppointmentOuter:
        outer = AppointmentOuter(
            **self.appointment.model_dump(),
            price=self._calculate_appointment_price()
        )
        return outer

    def _calculate_appointment_price(self) -> Decimal:
        price = self._calculate_total_price(
            self.service_constructor._calculate_price
        )
        return price

    def _calculate_total_price(self, calculate_price: Callable) -> Decimal:
        return sum(self._get_prices(calculate_price))

    def _get_prices(self, calculate_price: Callable) -> map:
        prices = map(
            lambda service: calculate_price(self.appointment.doctor_id, service),
            self._get_services()
        )
        return prices

    def _get_services(self) -> list[Service]:
        services = [
            link.service
            for link
            in self.appointment.appointment_links
        ]
        return services

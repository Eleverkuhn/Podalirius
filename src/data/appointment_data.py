from decimal import Decimal

from model.appointment_models import AppointmentOuter
from service.service_services import PriceCalculator, ServiceDataConstructor
from data.sql_models import Appointment, Service


class AppointmentDataConverter:
    """
    A set of utilites for conversion sqlmodel 'Appointment' to appointment
    pydantic models
    """
    def __init__(self, appointment: Appointment) -> None:
        self.appointment = appointment
        self.service_constructor = ServiceDataConstructor(appointment.doctor)

    def to_outer(self) -> AppointmentOuter:
        outer = AppointmentOuter(
            **self.appointment.model_dump(exclude=["patient_id"]),
            doctor=self.appointment.doctor.full_name,
            price=self._calculate_appointment_price()
        )
        return outer

    def _calculate_appointment_price(self) -> Decimal:
        total_price = sum(self._get_prices())
        return total_price

    def _get_prices(self) -> list[Decimal]:
        prices = [
            PriceCalculator(self.appointment.doctor, service).exec()
            for service
            in self._get_services()
        ]
        return prices

    def _get_services(self) -> list[Service]:
        services = [
            link.service
            for link
            in self.appointment.appointment_links
        ]
        return services

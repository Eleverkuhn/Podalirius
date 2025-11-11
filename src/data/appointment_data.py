from decimal import Decimal

from sqlmodel import Session, Sequence, select

from model.appointment_models import AppointmentOuter
from service.service_services import PriceCalculator, ServiceDataConstructor
from data.base_data import BaseCRUD
from data.sql_models import Patient, Appointment, Doctor, Service


class AppointmentCRUD(BaseCRUD):
    def __init__(
            self,
            session: Session,
            sql_model: type[Appointment] = Appointment,
            return_model: type[Appointment] = Appointment
    ) -> None:
        super().__init__(session, sql_model, return_model)
        self.related_models = [Doctor, Patient]

    @property
    def doctor_model(self) -> type[Doctor]:
        doctor_model = self.related_models[0]
        return doctor_model

    @property
    def doctor_select(self):
        statement = select(self.doctor_model)
        return statement

    @property
    def patient_model(self) -> Patient:
        patient_model = self.related_models[1]
        return patient_model

    def get_all_by_doctor(self, doctor_id: int) -> Sequence[Appointment]:
        statement = self.select.where(self.sql_model.doctor_id == doctor_id)
        result = self.session.exec(statement)
        appointments = result.all()
        return appointments


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

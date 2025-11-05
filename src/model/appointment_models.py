from datetime import date, time
from decimal import Decimal
from typing import Literal

from pydantic import Field

from model.base_models import AbstractModel
from data.base_data import FieldDefault


class AppointmentBase(AbstractModel):
    doctor_id: int
    date: date
    time: time


class AppointmentCreate(AppointmentBase):
    patient_id: bytes
    status: Literal["pending", "completed", "cancelled"] = "pending"
    is_paid: bool = Field(default=False)


class AppointmentInner(AppointmentCreate):
    id: int


class AppointmentOuter(AppointmentCreate):
    price: Decimal = Field(
        max_digits=FieldDefault.PRECISION,
        decimal_places=FieldDefault.SCALE
    )


class ServiceToAppointment(AbstractModel):
    appointment_id: int
    service_id: int

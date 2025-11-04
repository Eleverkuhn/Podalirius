from datetime import date, time
from typing import Literal

from pydantic import Field

from model.base_models import AbstractModel


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


class ServiceToAppointment(AbstractModel):
    appointment_id: int
    service_id: int

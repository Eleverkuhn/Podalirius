from datetime import datetime
from typing import Literal

from pydantic import Field

from model.base_models import Abs


class AppointmentBase(Abs):
    doctor_id: int
    date: datetime


class AppointmentCreate(AppointmentBase):
    patient_id: bytes
    status: Literal["pending", "completed", "cancelled"] = "pending"
    is_paid: bool = Field(default=False)


class Appointment(AppointmentCreate):
    id: int

from datetime import datetime
from typing import Literal

from pydantic import Field

from model.base_models import AbstractModel


class Appointment(AbstractModel):
    doctor_id: int
    patient_id: int
    date: datetime
    status: Literal["pending", "completed", "cancelled"]
    is_paid: bool = Field(default=False)

from datetime import time
from enum import Enum

from model.base_models import AbstractModel


class WeekdayEnum(str, Enum):
    monday = "1"
    tuesday = "2"
    wednesday = "3"
    thursday = "4"
    friday = "5"
    saturday = "6"
    sunday = "7"


class WorkSchedule(AbstractModel):
    doctor_id: int
    weekday: WeekdayEnum
    start_time: time
    end_time: time

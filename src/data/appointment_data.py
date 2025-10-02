from datetime import datetime
from typing import override

from pydantic import BaseModel
from sqlmodel import Field, Enum, Session

from model.appointment_models import Appointment, AppointmentCreate
from data.base_sql_models import BaseEnumSQLModel, BaseSQLModel
from data.crud import BaseCRUD


class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppointmentSQLModel(BaseEnumSQLModel, table=True):
    __tablename__ = "appointments"

    date: datetime
    status: Status
    is_paid: bool = Field(default=False)

    doctor_id: int = Field(foreign_key="doctors.id")
    patient_id: int = Field(foreign_key="patients.id")


class AppointmentCrud(BaseCRUD):
    def __init__(
            self,
            session: Session,
            sql_model=AppointmentSQLModel,
            return_model=Appointment) -> None:
        super().__init__(session, sql_model, return_model)

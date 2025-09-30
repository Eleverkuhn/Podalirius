from datetime import datetime
from typing import override

from pydantic import BaseModel
from sqlmodel import Field, Enum, Session

from model.appointment_models import Appointment
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
            sql_model: BaseSQLModel = AppointmentSQLModel,
            return_model: BaseModel = Appointment) -> None:
        super().__init__(session, sql_model, return_model)

    def create(self, data: dict) -> Appointment:
        created_appointment = super().create_raw_from_dict(data)
        appointment = self.return_model(**created_appointment.model_dump())
        return appointment

    @override
    def get_raw(self, id: int) -> Appointment:
        appointment = super().get_raw(id)
        return Appointment(**appointment.model_dump())

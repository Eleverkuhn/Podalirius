from datetime import datetime, date, time
from decimal import Decimal

from sqlmodel import Field, Enum

from data.base_sql_models import BaseSQLModel, PersonSQLModel, BaseEnumSQLModel

SERVICE_TITLE_MAX_LENGHT = 75
PRECISION = 8
SCALE = 2


class Specialty(BaseSQLModel, table=True):
    __tablename__ = "specialties"

    title: str = Field(max_length=30)
    description: None | str = Field(default=None)


class ServiceType(BaseSQLModel, table=True):
    __tablename__ = "services_types"

    title: str = Field(max_length=SERVICE_TITLE_MAX_LENGHT)
    price: Decimal = Field(max_digits=PRECISION, decimal_places=SCALE)


class Service(BaseSQLModel, table=True):
    __tablename__ = "services"

    title: str = Field(max_length=SERVICE_TITLE_MAX_LENGHT)
    description: None | str = Field(default=None)
    markup: None | Decimal = Field(
        default=0, max_digits=PRECISION, decimal_places=SCALE
    )

    type_id: int = Field(foreign_key="services_types.id")


class Doctor(PersonSQLModel, table=True):
    __tablename__ = "doctors"

    experience: date
    description: None | str = Field(default=None)


class Weekday(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class WorkSchedule(BaseEnumSQLModel, table=True):
    __tablename__ = "work_schedules"

    weekday: Weekday
    start_time: time
    end_time: time

    doctor_id: int = Field(foreign_key="doctors.id")


class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Appointment(BaseEnumSQLModel, table=True):
    __tablename__ = "appointments"

    date: datetime
    status: Status = Field(default=Status.PENDING)
    is_paid: bool = Field(default=False)

    doctor_id: int = Field(foreign_key="doctors.id")
    patient_id: int = Field(foreign_key="patients.id")


class ServiceToSpecialty(BaseSQLModel, table=True):
    __tablename__ = "services_to_specialties"

    service_id: int = Field(foreign_key="services.id")
    specialty_id: int | None = Field(
        default=None,
        foreign_key="specialties.id"
    )


class SpecialtyToDoctor(BaseSQLModel, table=True):
    __tablename__ = "specialties_to_doctors"

    doctor_id: int = Field(foreign_key="doctors.id")
    specialty_id: int = Field(foreign_key="specialties.id")


class ServiceToDoctor(BaseSQLModel, table=True):
    __tablename__ = "services_to_doctors"

    markup: None | Decimal = Field(
        default=0, max_digits=PRECISION, decimal_places=SCALE
    )

    doctor_id: int = Field(foreign_key="doctors.id")
    service_id: int = Field(foreign_key="services.id")


class ServiceToAppointment(BaseSQLModel, table=True):
    __tablename__ = "services_to_appointments"

    appointment_id: int = Field(foreign_key="appointments.id")
    service_id: int = Field(foreign_key="services.id")

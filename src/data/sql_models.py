from datetime import datetime, date, time
from decimal import Decimal
from uuid import uuid4

from sqlmodel import Field, Enum, Relationship

from data.base_data import (
    BaseSQLModel, BaseEnumSQLModel, FieldDefault, PersonSQLModel
)


class SpecialtyToDoctor(BaseSQLModel, table=True):
    __tablename__ = "specialties_to_doctors"

    doctor_id: int = Field(foreign_key="doctors.id")
    specialty_id: int = Field(foreign_key="specialties.id")


class DoctorToService(BaseSQLModel, table=True):
    __tablename__ = "doctors_to_services"

    markup: None | Decimal = Field(
        default=0,
        max_digits=FieldDefault.PRECISION,
        decimal_places=FieldDefault.SCALE
    )

    doctor_id: int = Field(foreign_key="doctors.id")
    service_id: int = Field(foreign_key="services.id")

    # doctor: "Doctor" = Relationship(back_populates="service_links")
    service: "Service" = Relationship(back_populates="doctor_links")


class DoctorToAppointment(BaseSQLModel, table=True):
    __tablename__ = "doctors_to_appointments"

    doctor_id: int = Field(foreign_key="doctors.id")
    appointment_id: int = Field(foreign_key="appointments.id")


class ServiceToSpecialty(BaseSQLModel, table=True):
    __tablename__ = "services_to_specialties"

    service_id: int = Field(foreign_key="services.id")
    specialty_id: int | None = Field(
        default=None,
        foreign_key="specialties.id"
    )


class ServiceToAppointment(BaseSQLModel, table=True):
    __tablename__ = "services_to_appointments"

    appointment_id: int = Field(foreign_key="appointments.id")
    service_id: int = Field(foreign_key="services.id")


class Specialty(BaseSQLModel, table=True):
    __tablename__ = "specialties"

    title: str = Field(max_length=30)
    description: None | str = Field(default=None)

    doctors: list["Doctor"] = Relationship(
        back_populates="specialties", link_model=SpecialtyToDoctor
    )
    services: list["Service"] = Relationship(
        back_populates="specialties", link_model=ServiceToSpecialty
    )


class Doctor(PersonSQLModel, table=True):
    __tablename__ = "doctors"

    experience: date
    description: None | str = Field(default=None)

    specialties: list["Specialty"] = Relationship(
        back_populates="doctors", link_model=SpecialtyToDoctor
    )
    services: list["Service"] = Relationship(
        back_populates="doctors", link_model=DoctorToService
    )
    work_days: list["WorkSchedule"] = Relationship(back_populates="doctors")
    appointments: list["Appointment"] = Relationship(
        back_populates="doctors", link_model=DoctorToAppointment
    )


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
    doctors: Doctor = Relationship(back_populates="work_days")


class ServiceType(BaseSQLModel, table=True):
    __tablename__ = "services_types"

    title: str = Field(max_length=FieldDefault.SERVICE_TITLE_MAX_LENGHT)
    price: Decimal = Field(
        max_digits=FieldDefault.PRECISION, decimal_places=FieldDefault.SCALE
    )

    services: list["Service"] = Relationship(back_populates="type")


class Service(BaseSQLModel, table=True):
    __tablename__ = "services"

    title: str = Field(max_length=FieldDefault.SERVICE_TITLE_MAX_LENGHT)
    description: None | str = Field(default=None)
    markup: None | Decimal = Field(
        default=0,
        max_digits=FieldDefault.PRECISION,
        decimal_places=FieldDefault.SCALE
    )

    type_id: int = Field(foreign_key="services_types.id")

    type: ServiceType = Relationship(back_populates="services")
    doctors: list["Doctor"] = Relationship(
        back_populates="services", link_model=DoctorToService
    )
    specialties: list["Specialty"] = Relationship(
        back_populates="services", link_model=ServiceToSpecialty
    )
    doctor_links: list[DoctorToService] = Relationship(back_populates="service")

    @property
    def price(self) -> Decimal:
        return self.markup + self.type.price


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

    doctors: list["Doctor"] = Relationship(
        back_populates="appointments", link_model=DoctorToAppointment
    )
    patient: "Patient" = Relationship(back_populates="appointments")


class Patient(PersonSQLModel, table=True):
    __tablename__ = "patients"

    id: bytes = Field(primary_key=True, default=uuid4().bytes)
    phone: str
    birth_date: date

    appointments: list["Appointment"] = Relationship(back_populates="patient")

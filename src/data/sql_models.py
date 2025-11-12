from datetime import date, time
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

    doctor: "Doctor" = Relationship(back_populates="doctor_links")
    service: "Service" = Relationship(back_populates="service_links")


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

    appointment: "Appointment" = Relationship(back_populates="appointment_links")
    service: "Service" = Relationship(back_populates="to_appointments_links")


class Specialty(BaseSQLModel, table=True):
    __tablename__ = "specialties"

    title: str = Field(max_length=FieldDefault.SPECIALTY_TITLE_MAX_LENGHT)
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
    work_days: list["WorkSchedule"] = Relationship(back_populates="doctors")
    appointments: list["Appointment"] = Relationship(back_populates="doctor")
    doctor_links: list[DoctorToService] = Relationship(back_populates="doctor")
    services: list["Service"] = Relationship(
        back_populates="doctors",
        sa_relationship_kwargs={
            "secondary": "doctors_to_services",
            "overlaps": "service,doctor,doctor_links"
        },
    )

    @property
    def full_name(self) -> str:
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}"
        return full_name

    @property
    def experience_in_years(self) -> int:
        years = date.today().year - self.experience.year
        return years


class Weekday(str, Enum):
    MONDAY = "0"
    TUESDAY = "1"
    WEDNESDAY = "2"
    THURSDAY = "3"
    FRIDAY = "4"
    SATURDAY = "5"
    SUNDAY = "6"


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
    specialties: list["Specialty"] = Relationship(
        back_populates="services", link_model=ServiceToSpecialty
    )
    service_links: list[DoctorToService] = Relationship(
        back_populates="service",
        sa_relationship_kwargs={"overlaps": "services"}
    )
    doctors: list["Doctor"] = Relationship(
        back_populates="services",
        sa_relationship_kwargs={
            "secondary": "doctors_to_services",
            "overlaps": "doctor,doctor_links,service,service_links"
        },
    )
    to_appointments_links: list[ServiceToAppointment] = Relationship(
        back_populates="service"
    )
    appointments: list["Appointment"] = Relationship(
        back_populates="services",
        sa_relationship_kwargs={
            "secondary": "services_to_appointments",
            "overlaps": "appointment,appointment_links,service,to_appointments_links"
        }
    )


class Status(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Patient(PersonSQLModel, table=True):
    __tablename__ = "patients"

    id: bytes = Field(primary_key=True, default=uuid4().bytes)
    phone: str
    birth_date: date

    appointments: list["Appointment"] = Relationship(
        back_populates="patient",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Appointment(BaseEnumSQLModel, table=True):
    __tablename__ = "appointments"

    date: date
    time: time
    status: Status = Field(default=Status.PENDING)
    is_paid: bool = Field(default=False)

    doctor_id: int = Field(foreign_key="doctors.id")
    patient_id: bytes = Field(foreign_key="patients.id")

    doctor: Doctor = Relationship(back_populates="appointments")
    patient: Patient = Relationship(back_populates="appointments")
    appointment_links: list[ServiceToAppointment] = Relationship(
        back_populates="appointment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    services: list["Service"] = Relationship(
        back_populates="appointments",
        sa_relationship_kwargs={
            "secondary": "services_to_appointments",
            "overlaps": "service,appointment,appointment_links,to_appointments_links"
        }
    )

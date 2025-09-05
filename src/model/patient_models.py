from uuid import UUID
from datetime import date

from pydantic import Field

from model.base_models import AbstractModel, PersonAbstract


class Patient(PersonAbstract):
    id: UUID
    birth_date: date
    phone: str = Field(min_length=10, max_length=10)


class PatientAdress(AbstractModel):
    patient_id: int
    city: str = Field(max_length=100)
    street: str = Field(max_length=100)
    building: int
    apartment: int


class PatientDocument(AbstractModel):
    appointment_id: int
    filename: str = Field(max_length=255)
    filetype: str = Field(max_length=255)
    filepath: str = Field(max_length=500)

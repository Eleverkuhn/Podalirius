from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, AfterValidator

from model.base_models import AbstractModel, PersonAbstract


def is_numeric(value: str) -> str:
    if not value.isnumeric():
        raise ValueError("Phone number is invalid")
    return value


class Phone(BaseModel):
    phone: Annotated[str, AfterValidator(is_numeric)] = Field(
        min_length=10, max_length=10)


class PatientCreate(PersonAbstract, Phone):
    birth_date: date


class PatientOuter(AbstractModel, PatientCreate):
    id: str


class PatientInner(PatientOuter):
    id: bytes


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

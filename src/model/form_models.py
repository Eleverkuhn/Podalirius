from datetime import date, datetime

from pydantic import BaseModel, Field


class PhoneForm(BaseModel):
    phone: str = Field(min_length=10, max_length=10)


class OTPCodeForm(BaseModel):
    value: None | str = Field(min_length=6, max_length=6)


class AppointmentBookingForm(BaseModel):
    last_name: str  # Take this fields from PatientModel
    middle_name: str
    first_name: str
    birth_date: date
    specialty: str  # Enum(ids)
    service: str  # Enum(ids)
    doctor: str   # Enum(ids)
    date: datetime

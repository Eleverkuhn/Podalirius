from datetime import datetime
from datetime import date

from pydantic import BaseModel, Field, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError

from model.appointment_models import AppointmentBase
from model.patient_models import PatientCreate, Phone


class PhoneForm(Phone):
    # TODO: implement as_form method
    pass


class OTPCodeForm(BaseModel):
    # TODO: implement as_form and empty methods
    value: None | str = Field(min_length=6, max_length=6)


class AppointmentBookingForm(AppointmentBase, PatientCreate):
    specialty_id: int
    service_id: int

    @classmethod
    def as_form(
            cls,
            last_name: str = Form(...),
            middle_name: str = Form(...),
            first_name: str = Form(...),
            birth_date: date = Form(...),
            phone: str = Form(...),
            specialty_id: int = Form(...),
            service_id: int = Form(...),
            doctor_id: int = Form(...),
            date: datetime = Form(...)) -> "AppointmentBookingForm":
        try:
            return cls(
                last_name=last_name,
                middle_name=middle_name,
                first_name=first_name,
                birth_date=birth_date,
                phone=phone,
                specialty_id=specialty_id,
                service_id=service_id,
                doctor_id=doctor_id,
                date=date)
        except ValidationError as exc:
            raise RequestValidationError(exc.errors())

    @classmethod
    def empty(cls) -> "AppointmentBookingForm":
        return cls.model_construct(
            last_name="",
            middle_name="",
            first_name="",
            birth_date=date.today(),
            phone="",
            specialty_id=0,
            service_id=0,
            doctor_id=0,
            date=datetime.now()
        )

    def get_patient_data(self) -> PatientCreate:
        return PatientCreate(**self.model_dump())

    def get_appointment_data(self) -> AppointmentBase:
        return AppointmentBase(**self.model_dump())

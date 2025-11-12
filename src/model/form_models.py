from datetime import date, time
from typing import override

from pydantic import Field, ValidationError
from fastapi import Form
from fastapi.exceptions import RequestValidationError

from model.appointment_models import AppointmentDateTime, AppointmentBase
from model.patient_models import PatientCreate, Phone


class PhoneForm(Phone):
    @classmethod
    def as_form(cls, phone: str = Form(...)) -> "PhoneForm":
        try:
            return cls(phone=phone)
        except ValidationError as exc:
            raise RequestValidationError(exc.errors())


class OTPCodeForm(PhoneForm):
    code: str = Field(min_length=6, max_length=6)

    @override
    @classmethod
    def as_form(
            cls, phone: str = Form(...), code: str = Form(...)
    ) -> "OTPCodeForm":
        try:
            return cls(phone=phone, code=code)
        except ValidationError as exc:
            raise RequestValidationError(exc.errors())


class AppointmentBookingForm(AppointmentBase, PatientCreate):
    specialty_id: int
    service_id: int

    def get_patient_data(self) -> PatientCreate:
        return PatientCreate(**self.model_dump())

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
            date: date = Form(...),
            time: time = Form(...)
    ) -> "AppointmentBookingForm":
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
                date=date,
                time=time
            )
        except ValidationError as exc:
            raise RequestValidationError(exc.errors())


class PatientUpdateForm(PatientCreate):
    @classmethod
    def as_form(
            cls,
            last_name: str = Form(...),
            middle_name: str = Form(...),
            first_name: str = Form(...),
            birth_date: date = Form(...),
            phone: str = Form(...),
    ) -> "PatientUpdateForm":
        try:
            return cls(
                last_name=last_name,
                middle_name=middle_name,
                first_name=first_name,
                birth_date=birth_date,
                phone=phone
            )
        except ValidationError as exc:
            raise RequestValidationError(exc.errors())


# class RescheduleAppointmentForm(AppointmentDateTime):  # TODO: remove this
#     @classmethod
#     def as_form(
#             cls, date: date = Form(...), time: time = Form(...)
#     ) -> "RescheduleAppointmentForm":
#         try:
#             return cls(date=date, time=time)
#         except ValidationError as exc:
#             raise RequestValidationError(exc.errors())

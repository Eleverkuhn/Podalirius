import pytest
from sqlmodel import Sequence

from service.doctor_services import DoctorDataConstructor
from data.sql_models import Doctor


@pytest.fixture
def doctor_data_constructor(doctors: Sequence[Doctor]) -> DoctorDataConstructor:
    return DoctorDataConstructor(doctors=doctors)


@pytest.fixture
def doctor_data_constructor_single(doctor: Doctor) -> DoctorDataConstructor:
    return DoctorDataConstructor(doctor=doctor)

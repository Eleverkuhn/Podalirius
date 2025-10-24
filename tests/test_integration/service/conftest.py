from pathlib import Path

import pytest
from sqlmodel import Session, Sequence

from service.doctor_services import DoctorDataConstructor
from data.crud import BaseCRUD
from data.sql_models import Doctor


@pytest.fixture
def doctor_service(session: Session) -> DoctorDataConstructor:
    return DoctorDataConstructor(session)


@pytest.fixture
def doctors(session: Session) -> Sequence[Doctor]:
    return BaseCRUD(session, Doctor, Doctor).get_all()


@pytest.fixture
def doctor(
        doctors: Sequence[Doctor], request: pytest.FixtureRequest
) -> Doctor:
    return doctors[request.param]

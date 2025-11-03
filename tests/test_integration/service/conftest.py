import pytest
from sqlmodel import Session

from service.doctor_services import DoctorDataConstructor


@pytest.fixture
def doctor_service(session: Session) -> DoctorDataConstructor:
    return DoctorDataConstructor(session)

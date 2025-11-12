import pytest
from sqlmodel import Session

from logger.setup import get_logger
from data.sql_models import Doctor
from data.doctor_data import DoctorCRUD


@pytest.fixture
def crud(session: Session) -> DoctorCRUD:
    crud = DoctorCRUD(session)
    return crud


class TestDoctorCRUD:
    @pytest.mark.parametrize("doctor", [0], indirect=True)
    def test_get(self, crud: DoctorCRUD, doctor: Doctor) -> None:
        doctor_db = crud.get(doctor.id)
        assert doctor_db
        get_logger().debug(doctor_db)

import pytest
from sqlmodel import Session, Sequence

from logger.setup import get_logger
from service.specialty_services import SpecialtyDataConstructor
from data.base_data import BaseCRUD
from data.sql_models import Specialty


@pytest.fixture
def specialties(session: Session) -> Sequence[Specialty]:
    specialties_crud = BaseCRUD(session, Specialty, Specialty)
    specialties = specialties_crud.get_all()
    return specialties


class TestSpecialtyDataConstructor:
    @pytest.fixture(autouse=True)
    def _constructor(
            self, session: Session, specialties: Sequence[Specialty]
    ) -> None:
        self.constructor = SpecialtyDataConstructor(session, specialties)

    def test_exec(self) -> None:
        dumped_specialties = self.constructor.exec()
        assert dumped_specialties
        get_logger().debug(dumped_specialties)

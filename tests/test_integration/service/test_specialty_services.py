import pytest
from sqlmodel import Session, Sequence

from logger.setup import get_logger
from service.specialty_services import SpecialtyDataConstructor
from data.crud import BaseCRUD
from data.sql_models import Specialty


@pytest.fixture
def service(session: Session) -> SpecialtyDataConstructor:
    return SpecialtyDataConstructor(session)


@pytest.fixture
def specialties(session: Session) -> Sequence[Specialty]:
    specialties = BaseCRUD(session, Specialty, Specialty).get_all()
    return specialties


class TestSpecialtyDataConstructor:
    def test_exec(self, service: SpecialtyDataConstructor) -> None:
        assert service.exec()

    def test__traverse(
            self,
            service: SpecialtyDataConstructor,
            specialties: Sequence[Specialty]
    ) -> None:
        result = service._traverse(specialties)
        assert result
        get_logger().debug(result)

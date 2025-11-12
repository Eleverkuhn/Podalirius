import pytest
from sqlmodel import Session

from data.sql_models import Specialty
from data.specialty_data import SpecialtyCRUD


@pytest.fixture
def crud(session: Session) -> SpecialtyCRUD:
    crud = SpecialtyCRUD(session)
    return crud


class TestSpecialtyCRUD:
    @pytest.mark.parametrize("specialty", [0], indirect=True)
    def test_get_by_title(
            self, crud: SpecialtyCRUD, specialty: SpecialtyCRUD
    ) -> None:
        specialty_db = crud.get_by_title(specialty.title)
        assert specialty_db.title == specialty.title

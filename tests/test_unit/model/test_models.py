import pytest
from pydantic import ValidationError, Field

from model.base_models import PersonAbstract, AbstractModel
from model.patient_models import Phone


class AbstractModelTest(AbstractModel):
    id: int
    desc: str


class AbsTestExpanded(AbstractModelTest):
    addition_field: str = Field(default="addition_field")


@pytest.fixture
def abs() -> AbstractModelTest:
    return AbstractModelTest(id=1, desc="test")


@pytest.fixture
def abs_expanded(abs: AbstractModelTest) -> AbsTestExpanded:
    return AbsTestExpanded(**abs.model_dump())


class TestAbstractModel:
    def test_is_submodel_returns_true(
            self,
            abs: AbstractModelTest,
            abs_expanded: AbsTestExpanded) -> None:
        assert abs.is_submodel(abs_expanded)

    def test_is_submodel_returns_false(
            self,
            abs: AbstractModelTest,
            abs_expanded: AbsTestExpanded) -> None:
        abs.desc = "modified_desc"
        assert abs.is_submodel(abs_expanded) is False


class TestPersonAbstract:
    def test_not_alphabetical_value_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            PersonAbstract(
                last_name="last",
                middle_name="middle2",
                first_name="first"
            )


class TestPhone:
    def test_not_numeric_value_raises_validation_error(self) -> None:
        with pytest.raises(ValidationError):
            Phone(phone="999999999q")

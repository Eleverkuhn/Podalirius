from datetime import datetime
from typing import Annotated, ItemsView

from pydantic import BaseModel, Field, AfterValidator


def is_alpha(value: str) -> str | None:
    if value is None:
        return value
    if not value.isalpha():
        raise ValueError("Field must be string type")
    return value


class AbstractModel(BaseModel):
    def is_submodel(self, to_compare: "AbstractModel") -> bool:
        return self.dumped_items <= to_compare.dumped_items

    @property
    def dumped_items(self) -> ItemsView:
        return self.model_dump().items()


class AbstractInner(AbstractModel):
    id: int
    created_at: datetime
    updated_at: datetime


class PersonAbstract(AbstractModel):
    last_name: Annotated[str | None, AfterValidator(is_alpha)] = Field(
        None, min_length=2, max_length=40
    )
    middle_name: Annotated[str | None, AfterValidator(is_alpha)] = Field(
        None, min_length=3, max_length=20
    )
    first_name: Annotated[str | None, AfterValidator(is_alpha)] = Field(
        None, min_length=2, max_length=40
    )

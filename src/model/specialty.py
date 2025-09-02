from pydantic import Field

from model.base import AbstractModel


class Specialty(AbstractModel):
    title: str = Field(max_length=30)
    description: str | None

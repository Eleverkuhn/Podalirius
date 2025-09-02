from typing import Literal

from pydantic import Field, condecimal

from model.base import AbstractModel


class Service(AbstractModel):
    title: str = Field(max_length=75)
    type: Literal["appointment", "lab test", "surgery"]
    description: str
    cost: condecimal(max_digits=8, decimal_places=2)

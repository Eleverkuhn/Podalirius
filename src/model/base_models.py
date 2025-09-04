from datetime import datetime

from pydantic import BaseModel, Field


class AbstractModel(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class PersonAbstract(AbstractModel):
    last_name: str = Field(max_length=40)
    middle_name: str = Field(max_length=20)
    first_name: str = Field(max_length=40)

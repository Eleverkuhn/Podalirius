from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import SQLModel, Field


class BaseSQLModel(SQLModel):
    id: None | int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class BaseEnumSQLModel(BaseSQLModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class PersonSQLModel(BaseSQLModel):
    last_name: str | None = Field(default=None)
    middle_name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)

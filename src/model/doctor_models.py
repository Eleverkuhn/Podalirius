from datetime import date

from pydantic import Field

from model.base_models import BaseModel


class DoctorOuter(BaseModel):
    full_name: str
    experience: date
    description: None | str = Field(default=None)
    consultations: list[dict[str, int]]

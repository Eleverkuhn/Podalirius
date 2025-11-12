from pydantic import Field

from model.base_models import BaseModel


class DoctorOuter(BaseModel):
    full_name: str
    experience_in_years: int
    description: None | str = Field(default=None)
    consultations: list[dict[str, int]]

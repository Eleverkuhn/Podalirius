from pydantic import Field

from model.base_models import BaseModel
from model.service_models import ServiceOuter


class DoctorOuterBase(BaseModel):
    id: int
    full_name: str
    experience_in_years: int
    description: None | str = Field(default=None)


class DoctorOuter(DoctorOuterBase):
    consultations: list[dict[str, int]]


class DoctorDetail(DoctorOuterBase):
    services: list[ServiceOuter]

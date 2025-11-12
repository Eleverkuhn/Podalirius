from pydantic import Field

from model.base_models import AbstractModel
from model.doctor_models import DoctorOuter
from data.base_data import FieldDefault


class SpecialtyOuter(AbstractModel):
    title: str = Field(max_length=FieldDefault.SPECIALTY_TITLE_MAX_LENGHT)
    description: None | str = Field(default=None)
    doctors: list[DoctorOuter]

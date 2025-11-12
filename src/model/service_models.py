from pydantic import Field

from model.base_models import BaseModel
from data.base_data import FieldDefault


class ServiceOuter(BaseModel):
    title: str = Field(max_length=FieldDefault.SERVICE_TITLE_MAX_LENGHT)
    price: int

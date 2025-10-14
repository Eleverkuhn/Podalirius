from pydantic import Field

from model.base_models import AbstractModel


class OTPCode(AbstractModel):
    patient_id: str
    value: str = Field(min_length=6, max_length=6)

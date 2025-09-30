from datetime import date

from model.base_models import AbstractModel, PersonAbstract


class Doctor(AbstractModel, PersonAbstract):
    experience: date
    description: str

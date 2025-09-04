from datetime import date

from model.base_models import PersonAbstract


class Doctor(PersonAbstract):
    experience: date
    description: str

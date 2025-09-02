from datetime import date

from model.base import PersonAbstract


class Doctor(PersonAbstract):
    experience: date
    description: str

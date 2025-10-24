from sqlmodel import Session

from model.appointment_models import Appointment
from data.base_data import BaseCRUD
from data import sql_models


class AppointmentCrud(BaseCRUD):  # REF: rename to `ApppointmentCRUD`
    def __init__(
            self,
            session: Session,
            sql_model=sql_models.Appointment,
            return_model=Appointment) -> None:
        super().__init__(session, sql_model, return_model)

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session

from logger.setup import get_logger
from exceptions import DataDoesNotMatch
from model.patient_models import PatientCreate, Patient
from data.patient_data import PatientCRUD


class PatientService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def check_input_data(self, patient_input_data: PatientCreate) -> Patient:
        """
        The method is used in `AppointmentBooking`. Part of logic of
        creating an appointment for unlogged_in user
        """
        patient_db = self._check_patient_exsits(patient_input_data.phone)
        get_logger().debug(patient_db)
        if patient_db is not None:
            self._compare(patient_db, patient_input_data)
            return patient_db
        else:
            get_logger().debug("registry clause")
            return self.registry(patient_input_data)

    def _check_patient_exsits(self, phone: str) -> Patient | None:
        try:
            patient = PatientCRUD(self.session)._get_by_phone(phone)
        except NoResultFound:
            return None
        else:
            return patient

    def _compare(
            self,
            db_data: Patient,
            input_data: PatientCreate) -> bool:
        if input_data.is_submodel(db_data):
            return True
        else:
            raise DataDoesNotMatch()

    def registry(self, create_data: PatientCreate) -> Patient:
        """
        Separate method created for possible scalability
        """
        patient = PatientCRUD(self.session).create(create_data)
        return patient

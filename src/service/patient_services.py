from sqlalchemy.exc import NoResultFound
from sqlmodel import Session

from exceptions.exc import DataDoesNotMatch
from model.patient_models import PatientCreate, PatientOuter
from data.patient_data import PatientCRUD


class PatientService:
    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    def crud(self) -> PatientCRUD:
        return PatientCRUD(self.session)

    def registry(self, create_data: PatientCreate) -> PatientOuter:
        """
        Separate method created for possible scalability
        """
        patient = self.crud.create(create_data)
        patient = self.crud.convert_to_patient_outer(patient)
        self.session.commit()
        return patient

    def construct_patient_data(self, patient_id: str) -> dict[str, str]:
        patient = self.crud.get(patient_id)
        return patient.model_dump(exclude=["id"])

    def check_input_data(  # TODO: better naming
            self, patient_input_data: PatientCreate) -> PatientOuter:
        """
        The method is used in `AppointmentBooking`. Part of logic of
        creating an appointment for unlogged_in user
        """
        patient_db = self.check_patient_exists(patient_input_data.phone)
        if patient_db is not None:
            self._compare(patient_db, patient_input_data)
            patient_inner = self.crud.convert_to_patient_inner(patient_db)
            return patient_inner
        else:
            patient = self.crud.create(patient_input_data)
            return patient

    def check_patient_exists(self, phone: str) -> PatientOuter | None:
        try:
            patient = self.crud.get_by_phone(phone)
        except NoResultFound:
            return None
        else:
            return patient

    @classmethod
    def _compare(
            cls, patient_db: PatientOuter, patient_input: PatientCreate
    ) -> bool:
        if patient_input.is_submodel(patient_db):
            return True
        else:
            raise DataDoesNotMatch()

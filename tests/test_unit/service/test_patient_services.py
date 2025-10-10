import pytest

from exceptions import DataDoesNotMatch
from model.patient_models import PatientCreate, PatientOuter
from service.patient_services import PatientService
from data.patient_data import PatientSQLModel, PatientCRUD


class TestPatientService:
    def build__compare_data(
            self, patient: PatientSQLModel
    ) -> tuple[PatientOuter, PatientCreate]:
        patient_db = PatientCRUD.convert_to_patient_outer(patient)
        patient_input = PatientCreate(**patient.model_dump())
        return patient_db, patient_input

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test__compare_returns_ture_for_correct_input(
            self, patient_sql_model: PatientSQLModel
    ) -> None:
        data_matches = PatientService._compare(
            *self.build__compare_data(patient_sql_model)
        )
        assert data_matches is True

    @pytest.mark.parametrize("patients_data", ["patient_1"], indirect=True)
    def test__compare_raises_error_if_input_does_not_match(
            self, patient_sql_model: PatientSQLModel
    ) -> None:
        patient_db, patient_input = self.build__compare_data(patient_sql_model)
        patient_input.first_name = "unmatchingfirstname"
        with pytest.raises(DataDoesNotMatch):
            PatientService._compare(patient_db, patient_input)

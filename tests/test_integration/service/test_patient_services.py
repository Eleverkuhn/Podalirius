import pytest
from sqlmodel import Session

from logger.setup import get_logger
from model.patient_models import PatientCreate
from service.patient_services import PatientService
from data.patient_data import PatientSQLModel


@pytest.fixture
def service(session: Session) -> PatientService:
    return PatientService(session)


@pytest.mark.parametrize(
    "test_data", ["test_patients.json"], indirect=True
)
@pytest.mark.usefixtures("test_data")
class TestPatientService:
    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test_check_returns_patient_data_if_all_the_checks_are_passed(  # TODO: test both workflow with registry and for existing user
            self,
            service: PatientService,
            test_entry: PatientSQLModel) -> None:
        create_data = PatientCreate(**test_entry.model_dump())
        patient = service.check_input_data(create_data)
        assert patient is not None
        get_logger().debug(patient)

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test_check_input_data_reach_registry_clause__if_no_patient_exists(
            self,
            service: PatientService,
            build_test_data: PatientCreate) -> None:
        patient = service.check_input_data(build_test_data)
        assert patient is not None
        service.session.rollback()

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test__check_existing_patient_returns_true(
            self,
            service: PatientService,
            test_entry: PatientSQLModel) -> None:
        patient_exists = service._check_patient_exsits(test_entry.phone)
        assert patient_exists is not None

    @pytest.mark.parametrize(
        "build_test_data", [(PatientSQLModel, "patient_1")], indirect=True
    )
    def test__check_non_existing_patient_returns_false(
            self,
            service: PatientService,
            build_test_data: PatientCreate) -> None:
        patient_exists = service._check_patient_exsits(build_test_data.phone)
        assert patient_exists is None

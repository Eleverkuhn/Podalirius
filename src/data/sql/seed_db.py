from pathlib import Path

from data import sql_models
from data.mysql import get_session
from utils import DatabaseSeeder

FIXTURE_DIR = Path(__file__).parent.joinpath("fixtures")

MODELS_TO_FIXTURES = {
    sql_models.Doctor: FIXTURE_DIR.joinpath("doctors.json"),
    sql_models.WorkSchedule: FIXTURE_DIR.joinpath("work_schedules.json"),
    sql_models.ServiceType: FIXTURE_DIR.joinpath("services_types.json"),
    sql_models.Service: FIXTURE_DIR.joinpath("services.json"),
    sql_models.Specialty: FIXTURE_DIR.joinpath("specialties.json"),
    sql_models.ServiceToSpecialty: FIXTURE_DIR.joinpath(
        "services_to_specialties.json"
    ),
    sql_models.SpecialtyToDoctor: FIXTURE_DIR.joinpath(
        "specialties_to_doctors.json"
    ),
    sql_models.ServiceToDoctor: FIXTURE_DIR.joinpath(
        "services_to_doctors.json"
    )
}

DatabaseSeeder(next(get_session()), MODELS_TO_FIXTURES).execute()

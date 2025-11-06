from pathlib import Path

from data.connections import MySQLConnection
from data import sql_models
from utils import DatabaseSeeder

FIXTURE_DIR = Path(__file__).parent.joinpath("fixtures")

MODELS_TO_FIXTURES = {
    sql_models.Patient: FIXTURE_DIR.joinpath("patients.json"),
    sql_models.Doctor: FIXTURE_DIR.joinpath("doctors.json"),
    sql_models.Appointment: FIXTURE_DIR.joinpath("appointments.json"),
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
    sql_models.DoctorToService: FIXTURE_DIR.joinpath(
        "doctors_to_services.json"
    ),
    sql_models.ServiceToAppointment: FIXTURE_DIR.joinpath(
        "services_to_appointments.json"
    )
}


def seed_db() -> None:
    session = next(MySQLConnection.get_session())
    DatabaseSeeder(session, MODELS_TO_FIXTURES).execute()


if __name__ == "__main__":
    seed_db()

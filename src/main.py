from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from config import Config
from exceptions import exc, handlers
from web import (
    appointment_routes,
    auth_routes,
    doctor_routes,
    index_routes,
    patient_routes,
    service_routes,
    specialty_routes,
)

Config.setup()

app = FastAPI()

app.include_router(appointment_routes.router)
app.include_router(auth_routes.login_router)
app.include_router(auth_routes.verify_code_router)
app.include_router(doctor_routes.router)
app.include_router(index_routes.router)
app.include_router(patient_routes.patient_appointments_router)
app.include_router(patient_routes.patient_info_router)
app.include_router(service_routes.router)
app.include_router(specialty_routes.router)

app.add_exception_handler(
    RequestValidationError, handlers.RequestValidationErrorHandler()
)
app.add_exception_handler(
    exc.FormInputError, handlers.FormInputErrHandler()
)

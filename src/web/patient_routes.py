from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

from web.routes import Prefixes

patient_appointments_router = APIRouter(prefix=f"{Prefixes.MY}/appointments")
patient_info_router = APIRouter(prefix=f"{Prefixes.MY}/info")


@cbv(patient_appointments_router)
class PatientAppointment:
    @patient_appointments_router.get(
        "/", name="all_appointments", status_code=status.HTTP_200_OK)
    def get_all(self) -> None:
        pass

    @patient_appointments_router.get(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def get(self) -> None:
        pass

    @patient_appointments_router.put(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

    @patient_appointments_router.patch(
        "/{id}", name="appointment", status_code=status.HTTP_200_OK)
    def cancel(self) -> None:
        pass


@cbv(patient_info_router)
class PatientInfo:
    @patient_info_router.get(
        "/", name="info", status_code=status.HTTP_200_OK)
    def get(self) -> None:
        pass

    @patient_info_router.put(
        "/", name="info", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

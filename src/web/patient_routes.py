from fastapi import APIRouter, status
from fastapi_utils.cbv import cbv

basic_prefix = "/my"
patient_appointments_router = APIRouter(prefix="/appointments")
patient_info_router = APIRouter(prefix="/info")


@cbv(patient_appointments_router)
class PatientAppointments:
    @patient_appointments_router.get("/", status_code=status.HTTP_200_OK)
    def get_all(self) -> None:
        pass

    @patient_appointments_router.get("/{id}", status_code=status.HTTP_200_OK)
    def get(self) -> None:
        pass

    @patient_appointments_router.put("/{id}", status_code=status.HTTP_200_OK)
    def update(self) -> None:
        pass

    @patient_appointments_router.patch("/{id}", status_code=status.HTTP_200_OK)
    def cansel(self) -> None:
        pass


@cbv(patient_info_router)
class PatientInfo:
    @patient_info_router.get("/", status_code=status.HTTP_200_OK)
    def get_patient_info(self) -> None:
        pass

    @patient_info_router.put("/", status_code=status.HTTP_200_OK)
    def update_patient_info(self) -> None:
        pass

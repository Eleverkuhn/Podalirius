from model.patient_models import Patient

class PatientRegistry:
    def __init__(self, patient: Patient):
        self.patient = patient

    def create_patient(self) -> Patient:
        pass

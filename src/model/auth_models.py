from model.patient_models import Phone


class OTPCode(Phone):
    code: bytes
    salt: bytes

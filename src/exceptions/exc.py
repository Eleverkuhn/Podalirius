class CustomError(Exception):
    pass


class FormInputError(CustomError):
    pass


class OTPCodeNotFound(CustomError):
    pass


class OTPCodeHashDoesNotMatch(CustomError):
    pass


class DataDoesNotMatch(CustomError):
    pass

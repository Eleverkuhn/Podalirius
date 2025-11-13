from fastapi import HTTPException, status


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


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail
        )


class AccessTokenExpired(HTTPException):
    def __init__(self, detail: str = "Access token is expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail
        )


class AppointmentNotFound(HTTPException):
    def __init__(self, detail: str = "Appointment not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

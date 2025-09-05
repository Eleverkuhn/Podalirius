from fastapi import Request, status
from fastapi.responses import RedirectResponse


class AppointmentBooking:
    def __init__(
            self, request: Request, access_code: None | str = None) -> None:  # TODO: Don't forget about form
        if access_code:
            self.patient = self.get_patient_from_db(access_code)
        self.response = RedirectResponse(
            url=request.app.url_path_for("main"),
            status_code=status.HTTP_303_SEE_OTHER
        )

    def get_patient_from_db(self, access_code: str) -> None:
        pass

    def check_user_is_logged_in(self) -> None:
        # TODO: If user is logged in change response from main to personal page
        pass

    def create_appointment(self) -> None:
        pass

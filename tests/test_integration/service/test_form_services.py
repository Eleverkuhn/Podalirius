import pytest
from sqlmodel import Session

from service.form_services import AppointmentBookingFormDataConstructor
from tests.test_integration.conftest import BasePatientTest


class MockRequest:
    def __init__(self, cookies: dict[str, str]) -> None:
        self.cookies = cookies


@pytest.fixture
def mock_request(cookies: dict[str, str]) -> MockRequest:
    mock_request = MockRequest(cookies)
    return mock_request


class TestAppointmentBookingFormDataConstructor(BasePatientTest):
    @pytest.fixture(autouse=True)
    def _constructor(self, session: Session, mock_request: MockRequest) -> None:
        self.constructor = AppointmentBookingFormDataConstructor(
            session, mock_request
        )

    def test_construct(self) -> None:
        content = self.constructor.exec()
        assert content

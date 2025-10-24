from sqlmodel import Session


class BaseService:
    def __init__(self, session: Session) -> None:
        self.session = session

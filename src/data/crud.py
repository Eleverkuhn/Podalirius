from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select

from data.base_sql_models import BaseSQLModel


class BaseCRUD:
    def __init__(
            self,
            session: Session,
            sql_model: BaseSQLModel | None = None,
            return_model: BaseModel | None = None) -> None:
        self.session = session
        self.sql_model = sql_model
        self.return_model = return_model  # TODO: probably need to remove this

    def create_raw(self, model: BaseModel) -> SQLModel:
        # TODO: remove this on the beneath one
        entry = self.sql_model(**model.model_dump())
        return self._add(entry)

    def create_raw_from_dict(self, data: dict) -> SQLModel:
        # TODO: this method should be main creation method
        entry = self.sql_model(**data)
        return self._add(entry)

    def get_raw(self, id: int | bytes) -> None:
        with self.session as session:
            statement = select(self.sql_model).where(self.sql_model.id == id)
            result = session.exec(statement)  # TODO:: don't like the naming 
            return result.one()

    def get_all(self) -> list[BaseSQLModel]:
        statement = select(self.sql_model)
        entries = self.session.exec(statement)
        return entries.all()

    def update_raw(self, id: str | int, data: dict) -> None:
        entry = self.get_raw(id)
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        return self._add(entry)

    def delete_raw(self, id: int | bytes) -> None:
        entry = self.get_raw(id)
        with self.session as session:
            session.delete(entry)
            session.commit()

    def _add(self, entry) -> None:
        with self.session as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
        return entry

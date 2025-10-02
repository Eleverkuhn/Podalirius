from datetime import datetime

from pydantic import BaseModel
from sqlmodel import SQLModel, Session, select

from data.base_sql_models import BaseSQLModel


class BaseCRUD:
    def __init__(
            self,
            session: Session,
            sql_model: type[BaseSQLModel]) -> None:
        self.session = session
        self.sql_model = sql_model
    
    def _create(self, instance: BaseSQLModel) -> BaseSQLModel:
        """
        No session.commit() bacause it will be used in the service layer
        inside transactions
        """
        self.session.add(instance)
        self.session.flush()
        return instance

    def _get(self, id: int | bytes) -> BaseSQLModel:
        statement = self.select.where(self.sql_model.id == id)
        entry = self.session.exec(statement)
        return entry.one()

    @property
    def select(self):
        return select(self.sql_model)

    def _get_all(self):
        return self.session.exec(self.select).all()

    def _update(self, entry: BaseSQLModel, data: dict) -> BaseSQLModel:
        data["updated_at"] = datetime.now()
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry = self._create(entry)
        self.session.commit()
        return entry

    def _delete(self, entry: BaseSQLModel) -> None:
        self.session.delete(entry)
        self.session.commit()

    def _convert_to_sql_model(self, data: dict) -> BaseSQLModel:
        return self.sql_model(**data)

    def create_raw(self, model: BaseModel) -> SQLModel:  # FIX: deprecated
        entry = self.sql_model(**model.model_dump())
        return self._add(entry)

    def create_raw_from_dict(self, data: dict) -> SQLModel:  # FIX: deprecated
        # TODO: this method should be main creation method
        entry = self.sql_model(**data)
        return self._add(entry)

    def get_raw(self, id: int | bytes) -> None:  # FIX: deprecated
        with self.session as session:
            statement = select(self.sql_model).where(self.sql_model.id == id)
            result = session.exec(statement)  # TODO:: don't like the naming 
            return result.one()

    def update_raw(self, id: str | int, data: dict) -> None:  # FIX: deprecated
        entry = self.get_raw(id)
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        return self._add(entry)

    def delete_raw(self, id: int | bytes) -> None:  # FIX: deprecated
        entry = self.get_raw(id)
        with self.session as session:
            session.delete(entry)
            session.commit()

    def _add(self, entry) -> None:  # FIX: depreacated
        with self.session as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
        return entry

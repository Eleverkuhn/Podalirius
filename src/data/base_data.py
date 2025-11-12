from datetime import datetime

from pydantic import ConfigDict, BaseModel
from sqlmodel import SQLModel, Field, Session, select


class FieldDefault:
    SERVICE_TITLE_MAX_LENGHT = 75
    PRECISION = 8
    SCALE = 2


class BaseSQLModel(SQLModel):
    id: None | int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class BaseEnumSQLModel(BaseSQLModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class PersonSQLModel(BaseSQLModel):
    last_name: str | None = Field(default=None)
    middle_name: str | None = Field(default=None)
    first_name: str | None = Field(default=None)


class BaseCRUD:
    def __init__(
            self,
            session: Session,
            sql_model: type[BaseSQLModel],
            return_model: type[BaseModel]) -> None:
        self.session = session
        self.sql_model = sql_model
        self.return_model = return_model

    def create(self, create_data: BaseModel) -> BaseModel:
        instance = self.sql_model(**create_data.model_dump())
        self._add(instance)
        return self.return_model(**instance.model_dump())

    def get(self, id: int | bytes) -> BaseModel:
        entry = self._get(id)
        return self.return_model(**entry.model_dump())

    def get_all(self):
        return self.session.exec(self.select).all()

    def update(self, id: int | bytes, data: dict) -> BaseModel:
        entry = self._get(id)
        self._update(entry, data)
        return self.return_model(**entry.model_dump())

    def _add(self, instance: BaseSQLModel) -> None:
        """
        No session.commit() bacause it will be used in the service layer
        inside transactions
        """
        self.session.add(instance)
        self.session.flush()

    def _get(self, id: int | bytes) -> BaseSQLModel:
        statement = self.select.where(self.sql_model.id == id)
        entry = self.session.exec(statement)
        return entry.one()

    @property
    def select(self):
        return select(self.sql_model)

    def _update(self, entry: BaseSQLModel, data: dict) -> BaseSQLModel:
        data["updated_at"] = datetime.now()
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        self._add(entry)
        self.session.commit()

    def _delete(self, entry: BaseSQLModel) -> None:
        self.session.delete(entry)
        self.session.commit()

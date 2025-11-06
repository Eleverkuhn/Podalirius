import base64
import json
from pathlib import Path

from sqlalchemy.orm.exc import ObjectDeletedError
from sqlmodel import Session, inspect

from logger.setup import get_logger
from data.base_data import BaseSQLModel, BaseCRUD
from data.sql_models import Patient, Appointment
from data.patient_data import PatientCRUD

type FixtureContent = dict[str, dict] | list[dict]


def read_fixture(fixture: Path) -> dict | list:
    with open(fixture) as file:
        content = json.load(file)
    return content


class DatabaseSeeder:
    def __init__(
            self,
            session: Session,
            models_to_fixtures: dict[type[BaseSQLModel], Path]
    ) -> None:
        self.session = session
        self.models_to_fixtures = models_to_fixtures

    def execute(self) -> None:
        for sql_model, fixture in self.models_to_fixtures.items():
            self._prepare_data(sql_model, fixture)
            self._populate()

    def _prepare_data(
        self, sql_model: type[BaseSQLModel], fixture: Path
    ) -> None:
        """Sets data which will be used in all other methods of the class"""
        self._set_id_key(sql_model)
        self.crud = BaseCRUD(self.session, sql_model, sql_model)
        self.content = read_fixture(fixture)

    def _set_id_key(self, sql_model: type[BaseSQLModel]) -> None:
        """
        Sets a flag with which will be possible to check whether id
        conversion is needed or not
        """
        if sql_model is Patient:
            self.key = "id"
        elif sql_model is Appointment:
            self.key = "patient_id"
        else:
            self.key = None

    def _populate(self) -> None:
        if self._fixture_is_dict:
            self._populate_from_dict()
        elif self._fixture_is_list:
            self._populate_from_list()

    @property
    def _fixture_is_dict(self) -> bool:
        return type(self.content) is dict

    @property
    def _fixture_is_list(self) -> bool:
        return type(self.content) is list

    def _populate_from_dict(self) -> None:
        for data in self.content.values():
            self._populate_table(data)

    def _populate_from_list(self) -> None:
        for data in self.content:
            self._populate_table(data)

    def _populate_table(self, data: dict) -> None:
        self._check_key_exists(data)
        self._create_entry(data)

    def _check_key_exists(self, data: dict) -> None:
        if self.key:
            self._convert_id(data)

    def _convert_id(self, data: dict) -> None:
        data[self.key] = base64.b64decode(data[self.key])

    def _create_entry(self, data: dict) -> None:
        instance = self.crud.sql_model(**data)
        self.crud.create(instance)
        self.crud.session.commit()


class SetUpTest:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_entry(self, entry: BaseSQLModel) -> BaseSQLModel:
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def create_multiple(self, entries: list[BaseSQLModel]) -> None:
        self.session.add_all(entries)
        self.session.commit()
        self._refresh_multiple(entries)

    def delete_multiple(self, data: list[BaseSQLModel]) -> None:
        for entry in data:
            self._delete_entry(entry)

    def delete_patient(self, phone: str) -> None:
        patient = PatientCRUD(self.session)._get_by_phone(phone)
        self.tear_down(patient)

    def tear_down(self, entry: BaseSQLModel) -> None:
        try:
            self._inspect(entry)
        except ObjectDeletedError:
            pass

    def _refresh_multiple(self, entries: list[BaseSQLModel]) -> None:
        for entry in entries:
            self.session.refresh(entry)
            # self.session.expunge(entry)

    def _inspect(self, entry: BaseSQLModel) -> None:
        try:
            state = inspect(entry)
            if state.persistent:
                self._delete_entry(entry)
        except ObjectDeletedError:
            pass

    def _delete_entry(self, entry: BaseSQLModel) -> None:
        self.session.delete(entry)
        self.session.commit()

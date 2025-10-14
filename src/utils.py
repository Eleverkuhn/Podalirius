import json
from pathlib import Path

from sqlalchemy import TextClause
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlmodel import Session, Table, text, inspect

from logger.setup import get_logger
from model.auth_models import OTPCode
from data.redis_config import redis_conn
from data.base_sql_models import BaseSQLModel
from data.crud import BaseCRUD
from data.patient_data import PatientCRUD


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
            crud = BaseCRUD(self.session, sql_model, sql_model)
            content = read_fixture(fixture)
            self._content_type_check(crud, content)

    def _content_type_check(
            self, crud: BaseCRUD, content: dict | list
    ) -> None:
        if type(content) is dict:  # REF: temporal solution
            for data in content.values():
                self._populate_table(crud, data)
        elif type(content) is list:
            for data in content:
                self._populate_table(crud, data)

    def _populate_table(self, crud: BaseCRUD, data: dict) -> None:
        instance = crud.sql_model(**data)
        crud.create(instance)
        crud.session.commit()


class SetUpTest:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_otp_code_by_patient_id(self, patient_id: str) -> OTPCode:
        otp_keys = redis_conn.keys("otp:*")
        for otp_code in otp_keys:
            id = redis_conn.get(otp_code)
            if id == patient_id:
                return OTPCode(value=otp_code[4:], patient_id=id)

    def create_entry(self, entry: BaseSQLModel) -> BaseSQLModel:
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

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


class DatabaseTruncator:  # REF: probably need to remove this
    _set_fk_0: TextClause = text("SET FOREIGN_KEY_CHECKS = 0;")
    _set_fk_1: TextClause = text("SET FOREIGN_KEY_CHECKS = 1;")  # TODO: this can be refactored

    def __init__(self, session: Session) -> None:
        self.session = session

    def reset_database(self) -> None:
        self.session.exec(self._set_fk_0)
        self._truncate_tables()
        self.session.exec(self._set_fk_1)

    def _truncate_tables(self) -> None:
        for table in reversed(BaseSQLModel.metadata.sorted_tables):
            statement = self._get_truncate_table_query_string(table)
            self.session.exec(text(statement))

    @staticmethod
    def _get_truncate_table_query_string(table: Table) -> TextClause:
        return text(f"TRUNCATE TABLE `{table.name}`;")

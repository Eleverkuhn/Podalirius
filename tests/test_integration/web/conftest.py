import pytest
from fastapi.testclient import TestClient
from fastapi import status
from sqlmodel import Session

from main import app
from data.crud import BaseCRUD

type FormData = dict[str, str | int]


@pytest.fixture(autouse=True)
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def get_all(session: Session, request) -> BaseCRUD:
    sql_model, return_model = request.param
    return BaseCRUD(session, sql_model, return_model).get_all()

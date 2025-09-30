from sqlalchemy import text

from data.mysql import get_session


def test_get_session() -> None:
    session = next(get_session())
    result = session.exec(text("SELECT 1;"))
    value = result.one()
    assert value == (1,)

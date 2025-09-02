from sqlalchemy import text

from data.mysql import get_session


def test_mysql_conn() -> None:
    session = get_session()
    with session:
        result = session.exec(text("SELECT 1;"))
        value = result.one()
        assert value == (1,)

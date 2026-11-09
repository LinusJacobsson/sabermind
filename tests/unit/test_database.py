from typing import Never

import psycopg
import pytest

from sabermind.database.database import Database
from sabermind.database.exceptions import ConnectionError, QueryError
from sabermind.schemas.xid import Xid


def test_operations_require_connection() -> None:
    db = Database()
    with pytest.raises(QueryError, match="not established"):
        db.execute_query("SELECT 1")
    with pytest.raises(QueryError, match="not established"):
        db.execute_command("SELECT 1")
    with pytest.raises(QueryError, match="not established"), db.transaction():
        pytest.fail("Disconnected transaction must not enter its body")
    db.disconnect()


def test_connection_failure_preserves_cause(monkeypatch: pytest.MonkeyPatch) -> None:
    cause = psycopg.OperationalError("Connection refused")

    def fail_connect(*args: object, **kwargs: object) -> Never:
        raise cause

    monkeypatch.setattr(psycopg, "connect", fail_connect)
    db = Database()
    with pytest.raises(ConnectionError, match="Connection refused") as error:
        db.connect()
    assert error.value.__cause__ is cause
    assert db.conn is None


@pytest.mark.parametrize("value", ["", "not-an-xid", "z" * 20, "0" * 19 + "1"])
def test_xid_rejects_invalid_identifiers(value: str) -> None:
    with pytest.raises(ValueError, match="Invalid Xid"):
        Xid.parse(value)

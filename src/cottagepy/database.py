from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
import sqlite3
from typing import Optional


Database = sqlite3.Connection
MaybeDB = Optional[Database]
_connection_cottage_db: MaybeDB = None


@contextmanager
def having_cottage_db(db: str | Path | Database) -> Iterator[None]:
    global _connection_cottage_db
    if _connection_cottage_db is not None:
        raise ValueError(
            "A database connection is already in place as cottage database; cannot change it."
        )

    if not db:
        raise ValueError("Invalid cottage DB.")
    elif isinstance(db, (str, Path)):
        _connection_cottage_db = sqlite3.connect(db)
        with closing(_connection_cottage_db):
            yield
    elif isinstance(db, Database):
        _connection_cottage_db = db
        yield
    else:
        raise TypeError(f"Wrong argument type: {type(db).__name__}")

    _connection_cottage_db = None


def _cottage_db(mdb: MaybeDB = None) -> Database:
    if mdb is None:
        if _connection_cottage_db is None:
            raise ValueError("The global cottage database reference has not been set yet.")
        return _connection_cottage_db
    else:
        return mdb


@contextmanager
def cursor(db: MaybeDB = None) -> Iterator[sqlite3.Cursor]:
    with _cottage_db(db) as dbx:
        with closing(dbx.cursor()) as cur:
            yield cur


__all__ = ["cursor", "Database", "MaybeDB", "having_cottage_db"]

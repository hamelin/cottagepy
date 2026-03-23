from collections.abc import Iterator
from contextlib import closing
from datetime import datetime
import pytest
import sqlite3

from cottagepy import Database, init_db


@pytest.fixture
def ts_ref() -> datetime:
    return datetime.fromisoformat("2026-03-15T22:48:56-05:00")


@pytest.fixture
def db_bare() -> Iterator[Database]:
    with closing(sqlite3.connect(":memory:")) as db_:
        yield db_


@pytest.fixture
def db(db_bare: Database, ts_ref: datetime) -> Database:
    return init_db(db_bare, ts_main=ts_ref)

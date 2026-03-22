from collections.abc import Iterator
from datetime import datetime
import pytest
import sqlite3

import cottagepy


@pytest.fixture
def ts_ref() -> datetime:
    return datetime.fromisoformat("2026-03-15T22:48:56-05:00")


@pytest.fixture
def db_bare() -> Iterator[cottagepy.Database]:
    with sqlite3.connect(":memory:") as db_:
        yield db_


@pytest.fixture
def db(db_bare: cottagepy.Database, ts_ref: datetime) -> cottagepy.Database:
    return cottagepy.init_db(db_bare, ts_main=ts_ref)

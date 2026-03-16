from datetime import datetime
import pytest
import sqlite3

import cottagepy


@pytest.fixture
def ts_main() -> datetime:
    return datetime.fromisoformat("2026-03-15T22:48:56-05:00")


@pytest.fixture
def db() -> cottagepy.Database:
    return sqlite3.connect(":memory:")


@pytest.fixture
def db_cottage(db: cottagepy.Database, ts_main: datetime) -> cottagepy.Database:
    return cottagepy.set_up(db, ts_main)

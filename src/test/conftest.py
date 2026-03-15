import pytest
import sqlite3

import cottagepy


@pytest.fixture
def db() -> cottagepy.Database:
    return sqlite3.connect(":memory:")


@pytest.fixture
def db_cottage(db: cottagepy.Database) -> cottagepy.Database:
    return cottagepy.set_up(db)

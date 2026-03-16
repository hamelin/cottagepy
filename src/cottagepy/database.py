from collections.abc import Iterator
from contextlib import closing, contextmanager
import sqlite3


Database = sqlite3.Connection


@contextmanager
def cursor(db: Database) -> Iterator[sqlite3.Cursor]:
    with closing(db.cursor()) as cur:
        yield cur

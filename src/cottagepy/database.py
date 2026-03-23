from collections.abc import Iterator
from contextlib import AbstractContextManager, closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Protocol


Database = sqlite3.Connection | Path | str


class _CottageDatabase(Protocol):
    def connect(self) -> AbstractContextManager[sqlite3.Connection]: ...


class _CottageDatabaseNotSet:
    def connect(self) -> AbstractContextManager[sqlite3.Connection]:
        raise ValueError("The global cottage database reference has not been set yet.")


@dataclass
class _CottageDatabasePermanent:
    dbx: sqlite3.Connection

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        yield self.dbx


@dataclass
class _CottageDatabaseReference:
    ref: str

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        with sqlite3.connect(self.ref) as dbx:
            yield dbx


COTTAGE: _CottageDatabase = _CottageDatabaseNotSet()


def set_cottage_db(db: Database) -> None:
    global COTTAGE
    if COTTAGE is None:
        if not db:
            raise ValueError("Invalid cottage DB.")
        elif db == ":memory:":
            COTTAGE = _CottageDatabasePermanent(sqlite3.connect(":memory:"))
        elif isinstance(db, sqlite3.Connection):
            COTTAGE = _CottageDatabasePermanent(db)
        else:
            COTTAGE = _CottageDatabaseReference(str(db))
    else:
        raise ValueError("The cottage DB can only be set once, and then it becomes immutable.")
    assert COTTAGE


@contextmanager
def connection(db: Database | None = None) -> Iterator[sqlite3.Connection]:
    match db:
        case None:
            with COTTAGE.connect() as dbx:
                yield dbx
        case sqlite3.Connection():
            yield db
        case str() | Path():
            with sqlite3.connect(str(db)) as dbx:
                yield dbx
        case _:
            raise RuntimeError("Unreachable")


@contextmanager
def cursor(db: Database | None = None) -> Iterator[sqlite3.Cursor]:
    with connection(db) as dbx, closing(dbx.cursor()) as cur:
        yield cur

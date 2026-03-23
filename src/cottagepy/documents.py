from datetime import datetime
import sqlite3

from .database import cursor, Database


def _set_up(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        create table if not exists _deltas_(
            document text not null,
            iso8601 text not null default(datetime('now', 'localtime')),
            version text,
            delta text not null
        );

        create table if not exists _metadata_(
            document text primary key,
            language text
        );
        """
    )


def add_delta(
    document: str,
    delta: str,
    db: Database | None = None,
    ts: datetime | None = None,
    version: str | None = None,
) -> None:
    if not document:
        raise ValueError("Document name cannot be an empty string")

    ts_ = ts or datetime.now()
    with cursor(db) as cur:
        _set_up(cur)
        cur.execute(
            """
            insert into _deltas_(document, iso8601, version, delta)
            values (:document, :iso8601, :version, :delta)
            """,
            {
                "document": document,
                "iso8601": ts_.isoformat(),
                "version": version,
                "delta": delta or "",
            },
        )


def set_metadata(document: str, language: str | None, db: Database | None = None) -> None:
    if not document:
        raise ValueError("Document name cannot be an empty string")

    with cursor(db) as cur:
        _set_up(cur)
        cur.execute(
            "insert into _metadata_(document, language) values(?, ?)",
            (document, language),
        )

from datetime import datetime
import sqlite3

from .database import cursor, Database


def _set_up(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        create table if not exists _code_(
            module text not null,
            iso8601 text not null default(datetime('now', 'localtime')),
            version text,
            delta text not null
        );
        """
    )


def add_delta(
    db: Database,
    module: str,
    delta: str,
    ts: datetime | None = None,
    version: str | None = None,
) -> None:
    if not module:
        raise ValueError("Module name cannot be an empty string")

    ts_ = ts or datetime.now()
    with cursor(db) as cur:
        _set_up(cur)
        cur.execute(
            """
            insert into _code_(module, iso8601, version, delta)
            values (:module, :iso8601, :version, :delta)
            """,
            {
                "module": module,
                "iso8601": ts_.isoformat(),
                "version": version,
                "delta": delta,
            },
        )

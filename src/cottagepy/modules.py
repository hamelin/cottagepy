from collections.abc import Sequence
from datetime import datetime
from packaging.requirements import Requirement
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


def get_requirements(db: Database) -> list[Requirement]:
    try:
        with cursor(db) as cur:
            cur.execute("select req from _requirements_")
            return [Requirement(req) for (req,) in cur]
    except sqlite3.Error:
        return []


def put_requirement(db: Database, req: str | Requirement) -> None:
    if isinstance(req, str):
        req = Requirement(req)
    with cursor(db) as cur:
        cur.executescript(
            """
            create table if not exists _requirements_(
                name text primary key unique not null,
                req text not null
            );
            """,
        )
        cur.execute(
            """
            insert into _requirements_(name, req)
            values (:name, :req)
            on conflict(name) do update set req = excluded.req
            """,
            {"name": req.name, "req": str(req)},
        )


def set_requirements(
    db: Database,
    reqs: Sequence[str | Requirement] | str,
) -> None:
    if isinstance(reqs, str):
        reqs = reqs.split()

    put_requirement(db, "dummy")  # Ensures the _requirements_ table exists.
    with cursor(db) as cur:
        cur.executescript("delete from _requirements_; vacuum;")

    for req in reqs:
        put_requirement(db, req)

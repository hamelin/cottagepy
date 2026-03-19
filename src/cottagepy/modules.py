from datetime import datetime, timezone
from packaging.requirements import Requirement
import sqlite3
from typing import cast

from .database import cursor, Database


def put(
    db: Database,
    name: str,
    code: str,
    spec: str | None = None,
    version: str | None = None,
    ts: datetime | None = None,
) -> None:
    if not name:
        raise ValueError("Name cannot be an empty string")

    ts_ = cast(datetime, ts or datetime.now())
    if not ts_.tzinfo:
        ts_ = ts_.replace(tzinfo=timezone.utc)

    with cursor(db) as cur:
        cur.executescript(
            """
            create table if not exists _resources_(
                name text not null,
                iso8601 text not null,
                content blob,
                constraint pkey primary key (name, iso8601) on conflict fail
            );

            create table if not exists _modules_(
                name text primary key,
                version text,
                spec text,
                resource not null references _resources_(rowid) on delete restrict
            );

            create view if not exists _code_ as
            select
                _modules_.name as name,
                content as code
            from _modules_
            inner join _resources_ on (_modules_.resource = _resources_.rowid);
            """
        )
        cur.execute(
            """
            insert into _resources_(name, iso8601, content)
            values (:name, :iso8601, :content)
            """,
            {
                "name": name,
                "iso8601": ts_.isoformat(),
                "content": code.encode("utf-8"),
            },
        )
        resource = cur.lastrowid
        cur.execute(
            """
            insert or replace into _modules_(name, resource)
            values (:name, :resource)
            """,
            {"name": name, "resource": resource},
        )


def get_requirements(db: Database) -> list[Requirement]:
    try:
        with cursor(db) as cur:
            cur.execute("select req from _requirements_")
            return [Requirement(req) for req, in cur]
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

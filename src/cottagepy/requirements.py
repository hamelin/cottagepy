from packaging.requirements import Requirement
from sqlite3 import Cursor

from .database import cursor, Database


def _init(cur: Cursor) -> None:
    cur.executescript(
        """
        create table if not exists _requirements_(
            requirement text not null,
            resolved text
        );
        """,
    )


def get(db: Database | None = None) -> list[str]:
    with cursor(db) as cur:
        _init(cur)
        cur.execute("select requirement from _requirements_")
        reqs = [r for r, in cur]
    if "cottagepy" not in {Requirement(r).name for r in reqs}:
        reqs.insert(0, "cottagepy")
    return reqs


def set(requirements: list[str], db: Database | None = None) -> None:
    with cursor(db) as cur:
        _init(cur)
        cur.execute("delete from _requirements_")
        cur.executemany(
            "insert into _requirements_(requirement) values (?)",
            [(r,) for r in (req.strip() for req in "\n".join(requirements).split()) if r],
        )

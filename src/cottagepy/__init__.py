from datetime import datetime
from difflib import unified_diff

from . import requirements as _requirements_
from .database import connection, cursor, Database  # noqa
from .modules import add_delta


ENTRY_POINT_INIT = """\
from cottagepy.repl import run

if __name__ == "__main__":
    run(cottage)
"""


def diff_strings(left: str, right: str) -> str:
    return "".join(unified_diff(left.splitlines(keepends=True), right.splitlines(keepends=True)))


_DELTA_INIT = diff_strings("", ENTRY_POINT_INIT)


def init_db(
    db: Database,
    requirements: list[str] = [],
    python: str | None = None,
    managed: bool = True,
    download_auto: bool = True,
    ts_main: datetime | None = None,
) -> Database:
    add_delta(
        db,
        module="__main__",
        ts=ts_main,
        delta=_DELTA_INIT,
    )
    _requirements_.set(db=db, requirements=requirements)
    _add_python_config(db=db, python=python, managed=managed, download_auto=download_auto)
    return db


def _add_python_config(
    db: Database | None = None,
    python: str | None = None,
    managed: bool = True,
    download_auto: bool = True,
) -> None:
    with cursor(db) as cur:
        cur.executescript(
            """
            create table if not exists _python_(
                python text,
                managed int,
                download_auto int
            );
            """,
        )
        cur.execute(
            """
            insert into _python_(python, managed, download_auto)
            values (:python, :managed, :download_auto)
            """,
            {
                "python": python,
                "managed": int(managed),
                "download_auto": int(download_auto),
            },
        )

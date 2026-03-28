from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from uv import find_uv_bin

from . import patch, requirements as _requirements_
from .database import cursor, Database
from .documents import add_delta, set_metadata
from ._log import log


ENTRY_POINT_INIT = """\
from cottagepy.repl import run

if __name__ == "__main__":
    run(cottage)
"""
_DELTA_INIT = patch.diff("", ENTRY_POINT_INIT)


def init_db(
    db: Database,
    requirements: list[str] = [],
    python: str | None = None,
    managed: bool | None = None,
    download_auto: bool | None = None,
    ts_main: datetime | None = None,
) -> Database:
    add_delta(
        db=db,
        document="__main__",
        ts=ts_main,
        delta=_DELTA_INIT,
    )
    set_metadata(db=db, document="__main__", language="python")
    _requirements_.set(db=db, requirements=requirements)
    _add_python_config(db=db, python=python, managed=managed, download_auto=download_auto)
    return db


def as_int_or_none(n: bool | None) -> int | None:
    if n is None:
        return n
    return int(n)


def _add_python_config(
    python: str | None,
    managed: bool | None,
    download_auto: bool | None,
    db: Database | None = None,
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
                "managed": as_int_or_none(managed),
                "download_auto": as_int_or_none(download_auto),
            },
        )


@contextmanager
def _requirements_file(db: Database | None = None, dir: Path | None = None) -> Iterator[Path]:
    with NamedTemporaryFile(suffix=".txt", dir=dir, mode="w+", encoding="utf-8") as file:
        for req in _requirements_.get(db=db):
            print(req, file=file)
        file.flush()
        yield Path(file.name)


def _python_options(db: Database | None = None) -> list[str]:
    options = []
    with cursor(db) as cur:
        cur.execute(
            """
            select python, managed, download_auto
            from _python_
            order by rowid desc
            limit 1
            """,
        )
        config = cur.fetchone()

    if config is None:
        log.warning(
            "No Python configuration present in cottage database; falling back to the trivial configuration."
        )
        return []
    python, managed, download_auto = config
    if python is not None:
        options.extend(["--python", python])
    if managed is not None:
        options.append("--managed-python" if managed else "--no-managed-python")
    if download_auto == 0:
        options.append("--no-python-downloads")
    return options


@contextmanager
def _cottage_invocation(
    db: Database | None = None, dir: Path | None = None
) -> Iterator[list[str]]:
    with _requirements_file(db=db, dir=dir) as path_req:
        yield [
            find_uv_bin(),
            "run",
            "--isolated",
            "--with-requirements",
            str(path_req),
            *_python_options(db=db),
            "-m",
            "cottagepy._entry_point",
        ]


__all__ = [
    "Database",
    "cursor",
    "init_db",
]

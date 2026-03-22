from datetime import datetime
from difflib import unified_diff

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


def set_up_db(db: Database, ts_main: datetime | None = None) -> Database:
    add_delta(
        db,
        module="__main__",
        ts=ts_main,
        delta=_DELTA_INIT,
    )
    return db

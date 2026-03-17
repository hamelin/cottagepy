from datetime import datetime

from .database import cursor, Database  # noqa
from .modules import put as put_module


ENTRY_POINT_INIT = """\
from cottagepy.repl import run

if __name__ == "__main__":
    run(cottage)
"""


def set_up_db(db: Database, ts_main: datetime | None = None) -> Database:
    put_module(
        db,
        name="__main__",
        code=ENTRY_POINT_INIT,
        ts=ts_main,
    )
    return db

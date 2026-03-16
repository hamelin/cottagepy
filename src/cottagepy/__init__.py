from contextlib import closing
from datetime import datetime, timezone
from sqlite3 import Connection
from typing import cast


Database = Connection


CODE_MAIN = """\
print("Welcome to my cottage!")
"""


def set_up(db: Database, ts_main: datetime | None = None) -> Database:
    ts = cast(datetime, ts_main or datetime.now())
    if not ts.tzinfo:
        ts = ts.replace(tzinfo=timezone.utc)

    with closing(db.cursor()) as cur:
        cur.executescript(
            """
            create table if not exists _modules_(
                name text,
                iso8601 text,
                version text,
                spec text,
                code text
            );

            create table if not exists _resources_(
                module references _modules_(rowid),
                content blob
            );

            create table if not exists _requirements_(
                spec text
            );
            """,
        )
        cur.execute(
            """
            insert into _modules_(name, iso8601, code)
            values ('__main__', :iso8601, :code)
            """,
            {"iso8601": ts.isoformat(), "code": CODE_MAIN},
        )
    return db

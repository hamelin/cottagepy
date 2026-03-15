from contextlib import closing
from sqlite3 import Connection


Database = Connection


def set_up(db: Database) -> Database:
    with closing(db.cursor()) as cur:
        cur.executescript(
            """
            create table if not exists _modules_(
                name text,
                version text,
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
    return db

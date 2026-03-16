from datetime import datetime
import pytest  # noqa

from cottagepy import (
    cursor,
    Database,
    ENTRY_POINT_INIT,
)


def test_db_setup(db: Database, ts_ref: datetime) -> None:
    with cursor(db) as cur:
        cur.execute(
            """
            with tables_cottage_py(name) as (
                values ('_modules_'), ('_resources_')
            )
            select type, sqlite_schema.name
            from sqlite_schema
            inner join tables_cottage_py on (
                sqlite_schema.name = tables_cottage_py.name
            )
            order by sqlite_schema.name
            """,
        )
        assert [
            ("table", "_modules_"),
            ("table", "_resources_"),
        ] == list(cur)
        cur.execute("select name, version, spec, resource from _modules_")
        assert [("__main__", None, None, 1)] == list(cur)
        cur.execute("select rowid, name, iso8601, content from _resources_")
        assert [
            (1, "__main__", ts_ref.isoformat(), ENTRY_POINT_INIT.encode("utf-8"))
        ] == list(cur)

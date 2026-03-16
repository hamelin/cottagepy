from contextlib import closing
from datetime import datetime
import pytest  # noqa

from cottagepy import CODE_MAIN, Database


def test_set_up_cottage(db_cottage: Database, ts_main: datetime) -> None:
    with closing(db_cottage.cursor()) as cur:
        cur.execute(
            """
            with tables_cottage_py(name) as (
                values ('_modules_'), ('_requirements_'), ('_resources_')
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
            ("table", "_requirements_"),
            ("table", "_resources_"),
        ] == list(cur)
        cur.execute(
            """
            select sum(num) from (
                select count(*) as num from _requirements_
                union
                select count(*) as num from _resources_
            )
            """,
        )
        assert [(0,)] == list(cur)
        cur.execute("select * from _modules_")
        assert [("__main__", ts_main.isoformat(), "", CODE_MAIN)] == list(cur)

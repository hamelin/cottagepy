from contextlib import closing
import pytest  # noqa

from cottagepy import Database


def test_set_up_cottage(db_cottage: Database) -> None:
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
                select count(*) as num from _modules_
                union
                select count(*) as num from _requirements_
                union
                select count(*) as num from _resources_
            )
            """,
        )
        assert [(0,)] == list(cur)

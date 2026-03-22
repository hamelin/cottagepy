from .database import cursor, Database


def set(requirements: list[str], db: Database | None = None) -> None:
    with cursor(db) as cur:
        cur.executescript(
            """
            create table if not exists _requirements_(
                spec text not null,
                resolved text
            );
            """,
        )
        cur.execute("delete from _requirements_")
        cur.executemany(
            "insert into _requirements_(spec) values (?)",
            [(r,) for r in (req.strip() for req in "\n".join(requirements).split()) if r],
        )

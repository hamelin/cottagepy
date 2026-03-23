import code
from collections.abc import Callable
from dataclasses import dataclass
import sqlite3
import sys
import warnings

from .database import cursor, Database


@dataclass
class _Config:
    banner: str | None = None
    exitmsg: str | None = None
    ps1: str | None = None
    ps2: str | None = None


def _gather_config(db: Database, id_config: int) -> _Config:
    try:
        for query_params, warning in [
            (
                (
                    """
                    select banner, exitmsg, ps1, ps2
                    from repl
                    where rowid = :id_config
                    limit 1
                    """,
                    dict(id_config=id_config),
                ),
                f"Cottage database table repl does not have config ID {id_config}; falling back to latest configuration.",
            ),
            (
                (
                    """
                    select banner, exitmsg, ps1, ps2
                    from repl
                    order by rowid desc
                    limit 1
                    """,
                ),
                "Cottage database repl does not carry any configuration. Falling back to defaults.",
            ),
        ]:
            with cursor(db) as cur:
                cur.execute(*query_params)  # type: ignore
                for banner, exitmsg, ps1, ps2 in cur:
                    return _Config(banner=banner, exitmsg=exitmsg, ps1=ps1, ps2=ps2)
                else:
                    if id_config > 0:
                        warnings.warn(warning)
    except sqlite3.Error:
        pass  # Fall back to defaults.

    return _Config(
        banner=f"CottagePy | Python {sys.version}",
        exitmsg="",
        ps1=None,
        ps2=None,
    )


def run(
    db: Database,
    id_config: int = 0,
    readfunc: Callable[[str], str] | None = None,
) -> dict:
    config = _gather_config(db, id_config)
    prompts = {attr: getattr(sys, attr) for attr in ["ps1", "ps2"] if hasattr(sys, attr)}
    try:
        if config.ps1 is not None:
            sys.ps1 = config.ps1
        if config.ps2 is not None:
            sys.ps2 = config.ps2
        d: dict = {}
        try:
            code.interact(
                banner=config.banner,
                readfunc=readfunc,
                local=d,
                exitmsg=config.exitmsg,
            )
        except SystemExit:
            pass
        return d
    finally:
        if "ps1" in prompts:
            sys.ps1 = prompts["ps1"]
        if "ps2" in prompts:
            sys.ps2 = prompts["ps2"]


def add_config(
    db: Database,
    banner: str | None = None,
    exitmsg: str | None = None,
    ps1: str | None = None,
    ps2: str | None = None,
) -> int:
    with cursor(db) as cur:
        cur.execute(
            """
            create table if not exists repl(
                banner text,
                exitmsg text,
                ps1 text,
                ps2 text
            )
            """,
        )
        cur.execute(
            """
            insert into repl(banner, exitmsg, ps1, ps2)
            values (:banner, :exitmsg, :ps1, :ps2)
            """,
            dict(banner=banner, exitmsg=exitmsg, ps1=ps1, ps2=ps2),
        )
        return cur.lastrowid or 0

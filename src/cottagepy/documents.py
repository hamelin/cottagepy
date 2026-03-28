from dataclasses import dataclass
from datetime import datetime, timezone
import sqlite3

from . import patch
from .database import cursor, MaybeDB


def _set_up(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        create table if not exists _metadata_(
            document text primary key,
            language text
        );

        create table if not exists _deltas_(
            document text not null,
            iso8601 text not null default(datetime('now', 'localtime')),
            version text,
            delta text not null
        );
        """
    )


def dt2iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(tzinfo=None).isoformat(sep=" ")


def iso2dt(iso8601: str) -> datetime:
    return datetime.fromisoformat(f"{iso8601}+00:00")


def add_delta(
    document: str,
    delta: str,
    db: MaybeDB = None,
    ts: datetime | None = None,
    version: str | None = None,
) -> None:
    if not document:
        raise ValueError("Document name cannot be an empty string")

    ts_ = ts or datetime.now(timezone.utc)
    with cursor(db) as cur:
        _set_up(cur)
        cur.execute(
            """
            insert into _deltas_(document, iso8601, version, delta)
            values (:document, :iso8601, :version, :delta)
            """,
            {
                "document": document,
                "iso8601": dt2iso(ts_),
                "version": version,
                "delta": delta or "",
            },
        )


def set_metadata(document: str, language: str | None, db: MaybeDB = None) -> None:
    if not document:
        raise ValueError("Document name cannot be an empty string")

    with cursor(db) as cur:
        _set_up(cur)
        cur.execute(
            """
            insert into _metadata_(document, language)
            values(?, ?)
            on conflict(document) do update set language = excluded.language
            """,
            (document, language),
        )


@dataclass
class Document:
    text: str
    language: str | None


def get_document(
    document: str, db: MaybeDB = None, version: str | None = None, ts: datetime | None = None
) -> Document:
    with cursor(db) as cur:
        if version is not None:
            if ts is not None:
                raise ValueError(
                    "Can limit document revisions either by timestamp or by version, but not both"
                )
            cur.execute(
                """
                select max(iso8601)
                from _deltas_
                where document = :document and version = :version
                """,
                dict(document=document, version=version),
            )
            (iso8601,) = cur.fetchone()
            ts_limit = iso2dt(iso8601)
        elif ts is None:
            ts_limit = datetime.now()
        else:
            ts_limit = ts

        cur.execute(
            """
            select delta
            from _deltas_
            where document = :document and iso8601 <= :iso8601
            order by iso8601
            """,
            dict(document=document, iso8601=dt2iso(ts_limit)),
        )
        text = ""
        for (delta,) in cur:
            text = patch.apply(text, delta)
        cur.execute("select language from _metadata_ where document = ?", (document,))
        (language,) = cur.fetchone()
        return Document(text=text, language=language)

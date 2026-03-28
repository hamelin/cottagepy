import pytest
import sqlite3
from textwrap import dedent

from cottagepy import (
    cursor,
    Database,
    diff_strings,
    documents,
    patch,
)


@pytest.fixture
def delta_hello() -> str:
    return diff_strings(
        "",
        dedent(
            """\
            if __name__ == "__main__":
                print("Hello world")
            """
        ),
    )


def test_add_delta_no_metadata(db: Database, delta_hello: str) -> None:
    documents.add_delta(
        db=db,
        document="test",
        delta=delta_hello,
    )
    with cursor(db) as cur:
        cur.execute("select distinct document from _deltas_ order by document")
        assert [("__main__",), ("test",)] == list(cur)
        cur.execute("select document, language from _metadata_")
        assert [("__main__", "python")] == list(cur)
        cur.execute("select language from _metadata_ where document = 'test'")
        assert [] == list(cur)


def test_replace_metadata(db: Database) -> None:
    with cursor(db) as cur:
        cur.execute("select document, language from _metadata_")
        assert [("__main__", "python")] == list(cur)

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                "insert into _metadata_(document, language) values ('__main__', 'not-happening')"
            )

    documents.set_metadata(db=db, document="__main__", language="plain")
    with cursor(db) as cur:
        cur.execute("select document, language from _metadata_")
        assert [("__main__", "plain")] == list(cur)


@pytest.mark.parametrize(
    "left,right",
    [
        (
            "",
            """\
            heyhey
            hoho
            """,
        ),
        (
            """\
            asdf qwerty
            zxcv heyhey hoho
            """,
            """\
            asdf qwerty
            zxcv heyhey hoho
            """,
        ),
        (
            """\
            asdf qwerty
            zxcv heyhey hoho
            """,
            """\
            asdf qwerty
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            One kitty to another
            and she got all the way over
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            Kitties, a limerick

            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over

            -- I don't count steps all that well
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            One kitty to another
            heyhey!
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            hoho!
            and she got all the way over
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            One kitty to another
            heyhey
            hoho
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
        ),
        (
            """\
            One kitty to another
            said I'd love to be yonder
            and then she got up
            and trotted and hop
            and she got all the way over
            """,
            """\
            One kitty to another
            said I'd love to be over
            and then she got up
            and trotted and hop
            and she got all the way yonder
            """,
        ),
    ],
)
def test_delta_apply_revert(left: str, right: str) -> None:
    left = dedent(left)
    right = dedent(right)
    delta = patch.diff(left, right)
    assert right == patch.apply(left, delta)
    assert left == patch.revert(right, delta)

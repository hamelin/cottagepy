from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime
import pytest  # noqa
import sys
import warnings

from cottagepy import (
    cursor,
    Database,
    _DELTA_INIT,
    init_db,
    repl,
)


@pytest.mark.parametrize(
    "requirements",
    [
        [],
        ["numpy\npandas\npyarrow\n", "requests>3\ntextual>=8,<9\n"],
    ],
)
def test_db_setup(db_bare: Database, ts_ref: datetime, requirements: list[str]) -> None:
    db = init_db(db_bare, requirements=requirements, ts_main=ts_ref)
    with cursor(db) as cur:
        cur.execute(
            """
            with sources_cottage_py(name) as (
                values ('_code_'), ('_requirements_')
            )
            select type, sqlite_schema.name
            from sqlite_schema
            inner join sources_cottage_py on (
                sqlite_schema.name = sources_cottage_py.name
            )
            order by sqlite_schema.name
            """,
        )
        assert [
            ("table", "_code_"),
            ("table", "_requirements_"),
        ] == list(cur)
        cur.execute("select module, iso8601, version, delta from _code_")
        assert [("__main__", ts_ref.isoformat(), None, _DELTA_INIT)] == list(cur)

        requirements_normalized = [
            r for r in (req.strip() for req in " ".join(requirements).split()) if r
        ]
        cur.execute("select spec, resolved from _requirements_")
        assert [(r, None) for r in requirements_normalized] == list(cur)


def test_redirection(capsys) -> None:
    print("heyhey on stdout")
    print("heyhey on stderr", file=sys.stderr)
    capture = capsys.readouterr()
    assert "heyhey on stdout\n" == capture.out
    assert "heyhey on stderr\n" == capture.err


def mock_input(inputs: Sequence[str]) -> Callable[[str], str]:
    it = iter(inputs)

    def input(prompt: str = "") -> str:
        print(prompt)
        try:
            return next(it)
        except StopIteration:
            raise EOFError()
            return ""

    return input


@pytest.fixture
def mock_interaction_repl() -> Callable[[str], str]:
    return mock_input(["print(", "'asdf')"])


def check_repl_output(capsys, out: str, err: str) -> None:
    capture = capsys.readouterr()
    assert capture.err == err
    assert capture.out == out


def test_repl_uninit(
    capsys,
    db: Database,
    mock_interaction_repl: Callable[[str], str],
) -> None:
    repl.run(db, readfunc=mock_interaction_repl)
    check_repl_output(
        capsys,
        out=f"{sys.ps1}\n{sys.ps2}\nasdf\n{sys.ps1}\n",
        err=f"CottagePy | Python {sys.version}\n\n",
    )


@pytest.fixture
def repl_config_single(db: Database) -> Database:
    repl.add_config(
        db,
        banner="Welcome to my cottage!",
        exitmsg="This is the end.",
        ps1="--> ",
        ps2="| ",
    )
    return db


@contextmanager
def checking_prompts_unchanged() -> Iterator[None]:
    prompts = {prompt: getattr(sys, prompt) for prompt in ["ps1", "ps2"] if hasattr(sys, prompt)}
    yield
    for prompt, orig in prompts.items():
        assert orig == getattr(sys, prompt)


def test_repl_defaults(
    capsys,
    repl_config_single: Database,
    mock_interaction_repl: Callable[[str], str],
) -> None:
    db = repl_config_single
    with checking_prompts_unchanged():
        repl.run(db, readfunc=mock_interaction_repl)
    check_repl_output(
        capsys,
        out="--> \n| \nasdf\n--> \n",
        err="Welcome to my cottage!\n\nThis is the end.\n",
    )


@pytest.fixture
def repl_config_multiple(repl_config_single: Database) -> tuple[Database, int]:
    db = repl_config_single
    id_config = repl.add_config(
        db,
        banner="Hear ye hear ye",
        exitmsg="",
        ps1="$ ",
        ps2="> ",
    )
    repl.add_config(
        db,
        banner="Ignored\n",
    )
    return db, id_config


def test_repl_selected(
    capsys,
    repl_config_multiple: tuple[Database, int],
    mock_interaction_repl: Callable[[str], str],
) -> None:
    db, id_config = repl_config_multiple
    with checking_prompts_unchanged():
        repl.run(db, id_config=id_config, readfunc=mock_interaction_repl)
    check_repl_output(
        capsys,
        out="$ \n> \nasdf\n$ \n",
        err="Hear ye hear ye\n\n",
    )


def test_repl_set_variables(db: Database) -> None:
    assert {
        "a": 5,
        "b": "asdf",
        "__builtins__": __builtins__,
    } == repl.run(
        db, readfunc=mock_input(["b = 'asdf'", "a = 5"])
    )


@pytest.mark.parametrize(
    "expected,sql",
    [
        (
            ["does not have config ID 333"],
            "",
        ),
        (
            ["does not have config ID 333", "does not carry any configuration"],
            "delete from repl",
        ),
    ],
)
def test_warning_missing_config(
    expected: list[str],
    sql: str,
    repl_config_single: Database,
    mock_interaction_repl: Callable[[str], str],
) -> None:
    db = repl_config_single
    with cursor(db) as cur:
        cur.execute(sql)

    with warnings.catch_warnings(record=True) as ws:
        repl.run(db, id_config=333, readfunc=mock_interaction_repl)

    assert len(expected) == len(ws)
    for ex, w in zip(expected, ws):
        assert ex in str(w.message)

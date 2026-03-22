from argparse import Namespace
from pathlib import Path
import pytest

from cottagepy.__main__ import parse_args


@pytest.mark.parametrize(
    "expected,args",
    [
        (Namespace(command="init", file=Path("cot.db")), ["init", "cot.db"]),
        (
            Namespace(command="run", file=Path("cot.db"), entry_point="__main__", args=[]),
            ["run", "cot.db"],
        ),
        (
            Namespace(command="run", file=Path("ctg.db"), entry_point="asdf", args=[]),
            ["run", "-e", "asdf", "ctg.db"],
        ),
        (
            Namespace(
                command="run",
                file=Path("ctg.db"),
                entry_point="__main__:alt",
                args=[],
            ),
            ["run", "ctg.db", "--entry-point=__main__:alt"],
        ),
        (
            Namespace(
                command="run",
                file=Path("hey.db"),
                entry_point="__main__",
                args=["heyhey", "hoho"],
            ),
            ["run", "hey.db", "heyhey", "hoho"],
        ),
        (
            Namespace(
                command="run",
                file=Path("hey.db"),
                entry_point="__main__",
                args=["-e", "__main__:hey"],
            ),
            ["run", "hey.db", "--", "-e", "__main__:hey"],
        ),
    ],
)
def test_parse_args_legal(expected: Namespace, args: list[str]) -> None:
    assert expected == parse_args(args)


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["init"],
        ["run"],
        ["hey"],
    ],
)
def test_parse_args_illegal(args: list[str]) -> None:
    with pytest.raises(SystemExit):
        parse_args(args)

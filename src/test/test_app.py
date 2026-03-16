from argparse import Namespace
from pathlib import Path
import pytest

from cottagepy.__main__ import parse_args


@pytest.mark.parametrize(
    "expected,args",
    [
        (Namespace(command="setup", file=Path("cot.db")), ["setup", "cot.db"]),
        (Namespace(command="run", file=Path("cot.db")), ["run", "cot.db"]),
    ],
)
def test_parse_args_legal(expected: Namespace, args: list[str]) -> None:
    assert expected == parse_args(args)


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["setup"],
        ["run"],
        ["hey"],
    ],
)
def test_parse_args_illegal(args: list[str]) -> None:
    with pytest.raises(SystemExit):
        parse_args(args)

from argparse import Namespace
from collections.abc import Iterator
import io
from pathlib import Path
import pytest
import sys

from cottagepy.__main__ import parse_args


@pytest.fixture
def file_requirements(tmp_path: Path) -> Path:
    path_req = tmp_path / "requirements.txt"
    path_req.write_text("numpy\npandas\npyarrow\n", encoding="utf-8")
    return path_req


@pytest.fixture
def stdin_requirements() -> Iterator[None]:
    stdin_old = sys.stdin
    try:
        sys.stdin = io.StringIO("requests>3\ntextual>=8,<9\n")
        yield None
    finally:
        sys.stdin = stdin_old


@pytest.mark.parametrize(
    "expected,args",
    [
        (Namespace(command="init", file=Path("cot.db"), requirements=[]), ["init", "cot.db"]),
        (
            Namespace(command="init", file=Path("cot.db"), requirements=["numpy"]),
            ["init", "--with", "numpy", "cot.db"],
        ),
        (
            Namespace(command="init", file=Path("cot.db"), requirements=["numpy"]),
            ["init", "-w", "numpy", "cot.db"],
        ),
        (
            Namespace(
                command="init",
                file=Path("cot.db"),
                requirements=["numpy", "pandas", "requests aiosqlite"],
            ),
            ["init", "-w", "numpy", "--with", "pandas", "cot.db", "-w", "requests aiosqlite"],
        ),
        (
            Namespace(
                command="init",
                file=Path("cot.db"),
                requirements=["numpy\npandas\npyarrow\n"],
            ),
            ["init", "-r", "{requirements_file}", "cot.db"],
        ),
        (
            Namespace(
                command="init", file=Path("cot.db"), requirements=["numpy\npandas\npyarrow\n"]
            ),
            ["init", "cot.db", "--requirements", "{requirements_file}"],
        ),
        (
            Namespace(
                command="init",
                file=Path("cot.db"),
                requirements=[
                    "numpy\npandas\npyarrow\n",
                    "requests>3\ntextual>=8,<9\n",
                ],
            ),
            ["init", "cot.db", "--requirements", "{requirements_file}", "-r", "-"],
        ),
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
def test_parse_args_legal(
    expected: Namespace,
    args: list[str],
    file_requirements: Path,
    stdin_requirements: None,
) -> None:
    assert expected == parse_args([
        arg.format(requirements_file=str(file_requirements)) for arg in args
    ])


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

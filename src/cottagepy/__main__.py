from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
import sqlite3
import sys

from . import init_db


def _requirements_file(path_: str) -> str:
    with (sys.stdin if path_ == "-" else open(path_, mode="r", encoding="utf-8")) as file:
        return file.read()


def parse_args(args: Sequence[str] | None = None) -> Namespace:
    parser = ArgumentParser(
        description="""
            CottagePy - Your own little computational cottage
        """,
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands",
    )

    cmd_init = subparsers.add_parser(
        "init",
        help="Set up a new cottage database.",
        description="Set up a new cottage database.",
    )
    cmd_init.add_argument(
        "file",
        type=Path,
        help="Path to the cottage database to set up.",
    )
    cmd_init.set_defaults(requirements=[])
    cmd_init.add_argument(
        "-w",
        "--with",
        action="append",
        dest="requirements",
        help="""
            Add constraints to the cottage's dependency requirements. Can be used more than once.
        """,
    )
    cmd_init.add_argument(
        "-r",
        "--requirements",
        action="append",
        type=_requirements_file,
        dest="requirements",
        help="""
            Append the contents of the given file to the cottage's dependency requirements.
            If the given path is -, standard input is read for package specifications.
            Can be used more than once (with different files, presumably).
        """,
    )
    cmd_init.add_argument(
        "-p",
        "--python",
        help="Set the Python version or interpreter path to use when running this cottage.",
    )
    cmd_init.set_defaults(managed_python=True)
    cmd_init.add_argument(
        "--managed-python",
        action="store_true",
        dest="managed_python",
        help="""
            Enable usage of a UV-managed Python interpreter if CottagePy is allowed to choose.
            This is the default.
        """,
    )
    cmd_init.add_argument(
        "--no-managed-python",
        action="store_false",
        dest="managed_python",
        help="Disable usage of UV-managed Python interpreters.",
    )
    cmd_init.add_argument(
        "--no-python-downloads",
        action="store_false",
        dest="python_downloads",
        default=True,
        help="""
            If usage of UV-managed Python interpreters is enabled, this forbids downloading new
            ones automatically.
        """,
    )

    cmd_run = subparsers.add_parser(
        "run",
        help="Run a cottage.",
        description="Run a cottage.",
    )
    cmd_run.add_argument(
        "file",
        type=Path,
        help="Path to cottage database to run.",
    )
    cmd_run.add_argument(
        "-e",
        "--entry-point",
        help="Set an alternative entry point (default is the __main__ module of the cottage database).",
        default="__main__",
    )
    cmd_run.add_argument(
        "args",
        nargs="*",
        default=[],
        help="Arguments passed to the cottage's entry point.",
    )

    ns = parser.parse_args(args)
    if ns.command is None:
        parser.print_help()
        sys.exit(1)
    return ns


def main() -> None:
    ns = parse_args()
    match ns.command:
        case "init":
            with sqlite3.connect(ns.file) as db:
                init_db(db)

        case "run":
            raise NotImplementedError()

        case _:
            raise RuntimeError(f"Unknown command: {ns.command}")


if __name__ == "__main__":
    main()

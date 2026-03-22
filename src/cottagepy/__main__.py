from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
import sqlite3
import sys

from . import init_db


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

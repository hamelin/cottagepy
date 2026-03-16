from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path
import sqlite3
import sys

from . import set_up


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

    cmd_setup = subparsers.add_parser(
        "setup",
        help="Set up a new cottage database.",
        description="Set up a new cottage database.",
    )
    cmd_setup.add_argument(
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

    ns = parser.parse_args(args)
    if ns.command is None:
        parser.print_help()
        sys.exit(1)
    return ns


def main() -> None:
    ns = parse_args()
    match ns.command:
        case "setup":
            with sqlite3.connect(ns.file) as db:
                set_up(db)

        case "run":
            raise NotImplementedError()

        case _:
            raise RuntimeError(f"Unknown command: {ns.command}")


if __name__ == "__main__":
    main()

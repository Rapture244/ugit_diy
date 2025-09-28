#!/usr/bin/env python3
# !INFO: src/ugit_diy/cli.py
"""Command-line interface for ugit_diy.

Parses arguments and dispatches to command handlers.
"""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
import argparse
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version as _v
import sys

# from typing import TYPE_CHECKING
# local
from ugit_diy.__init__ import __version__

# --------------------------------------------------- BASEDPYRIGHT --------------------------------------------------- #
# Imported only for static checkers; not used at runtime.
# if TYPE_CHECKING:


# ==================================================================================================================== #
#                                                       CONSTANTS                                                      #
# ==================================================================================================================== #
# Distribution/package metadata
# IMPORTANT: Must match the `[project].name` field in pyproject.toml.
DIST_NAME = "ugit-diy"


# ==================================================================================================================== #
#                                                   PARSER CONSTRUCTION                                                #
# ==================================================================================================================== #
def _build_parser() -> argparse.ArgumentParser:
    """Build the main CLI parser (UV-style) with global options only."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="ugit",
        description="A tiny Git-like version control system for learning Git.",
        usage="%(prog)s [OPTIONS]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,  # suppress auto-help, we add it in the group
        allow_abbrev=False,  # avoid accidental abbrevs (e.g. --ver → --version)
        exit_on_error=True,
        epilog="Use '%(prog)s --help' for more details.",
    )

    # ------- resolve version string ------- #
    # Prefer installed distribution metadata, fall back to __version__ for local dev.
    try:
        shown_version = f"{DIST_NAME} v{_v(DIST_NAME)}"
    except PackageNotFoundError:
        shown_version = f"{DIST_NAME} v{__version__}"

    # ------- global options (UV-style group) ------- #
    global_opts = parser.add_argument_group("Global options")

    _ = global_opts.add_argument(
        "-h",
        "--help",
        action="help",
        help="Display the concise help for this command",
    )
    _ = global_opts.add_argument(
        "-v",
        "--version",
        action="version",
        version=shown_version,
        help=f"Display the {DIST_NAME} version",
    )
    return parser


# ==================================================================================================================== #
#                                                        DISPATCH                                                      #
# ==================================================================================================================== #
# TODO: Future subcommands will be added here (e.g. `init`, `commit`, `log`, etc.).
def _dispatch(_ns: argparse.Namespace) -> int:
    """Route to subcommands based on parsed args. No subcommands yet → succeed."""
    return 0


# ==================================================================================================================== #
#                                                         MAIN                                                         #
# ==================================================================================================================== #
def main(argv: Sequence[str] | None = None) -> int:
    """Parse args and return an exit code (no sys.exit here).

    Tests call `main([...])` directly; no global sys.argv patching. We also convert argparse's
    SystemExit into an int exit code for simple assertions.
    """
    parser: argparse.ArgumentParser = _build_parser()

    # No args → print help to stdout and return 0
    if not argv:
        parser.print_help()
        return 0

    try:
        ns: argparse.Namespace = parser.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code is None else int(e.code)

    return _dispatch(ns)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

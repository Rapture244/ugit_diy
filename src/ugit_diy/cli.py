#!/usr/bin/env python3
# !INFO: src/ugit_diy/cli.py


# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stlib
import argparse
from importlib.metadata import PackageNotFoundError, version as _v

# local
from . import __version__

# ==================================================================================================================== #
#                                                       CONSTANTS                                                      #
# ==================================================================================================================== #
# Distribution/package metadata
# IMPORTANT: Must match the `[project].name` field in pyproject.toml.
DIST_NAME = "ugit-diy"


# ==================================================================================================================== #
#                                                        CLI ARG                                                       #
# ==================================================================================================================== #

# ------------------------------------------------- COMMAND HANDLERS ------------------------------------------------- #
# TODO: Future subcommands will be added here (e.g. `init`, `commit`, `log`, etc.)


# ------------------------------------------------------ PARSER ------------------------------------------------------ #


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments.

    Builds the main CLI parser (UV-style) with global options only.
    Returns the parsed arguments namespace.
    """
    # ------- main parser (top-level) ------- #
    parser = argparse.ArgumentParser(
        prog="ugit",
        description="A tiny Git-like version control system for learning.",
        usage="%(prog)s [OPTIONS]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,  # suppress auto-help, we'll define it manually in global options
        allow_abbrev=False,  # avoid accidental option abbreviations (e.g. `--ver` → `--version`)
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

    global_opts.add_argument(
        "-h",
        "--help",
        action="help",
        help="Display the concise help for this command",
    )
    global_opts.add_argument(
        "-v",
        "--version",
        action="version",
        version=shown_version,
        help=f"Display the {DIST_NAME} version",
    )

    # ------- parse & post-process ------- #
    args = parser.parse_args()

    # If invoked with no options at all, show the help (UV shows guidance by default).
    if not vars(args):
        parser.print_help()
        parser.exit(0)

    return args


# ==================================================================================================================== #
#                                                         MAIN                                                         #
# ==================================================================================================================== #


def main() -> None:
    """Entry point for the CLI."""
    parse_args()


if __name__ == "__main__":
    main()

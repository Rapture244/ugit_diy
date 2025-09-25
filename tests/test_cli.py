# tests/test_cli.py
"""Basic CLI tests for 'ugit' help behavior with no arguments."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
from __future__ import annotations

from typing import TYPE_CHECKING

# 3rd party
# local
from ugit_diy import __version__

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.conftest import CliResult


# ==================================================================================================================== #
#                                                         TESTS                                                        #
# ==================================================================================================================== #
def test_cli_no_args(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running the cli with no args prints help to stdout and exits with code 0."""
    code, out, err = run_cli(["ugit"])

    assert code == 0
    assert "usage: ugit" in out
    assert "Global options" in out
    assert err == ""


def test_cli_help_option(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running `ugit --help` prints help text and exits with code 0."""
    code, out, err = run_cli(["ugit", "--help"])

    assert code == 0
    assert "usage: ugit" in out
    assert "Global options" in out
    assert err == ""


def test_cli_version_option(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running `ugit --version` prints the version and exits with code 0."""
    _, out, err = run_cli(["ugit", "--version"])

    expected: str = f"ugit-diy v{__version__}\n"  # argparse adds a trailing newline
    assert out == expected
    assert err == ""

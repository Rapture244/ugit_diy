# tests/test_cli.py
"""Basic CLI tests for 'ugit' help behavior with no arguments."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
from __future__ import annotations

from typing import TYPE_CHECKING

# 3rd party
import pytest

# local
from ugit_diy import __version__

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Callable

    from _pytest.mark import MarkDecorator
    from tests.conftest import CliResult

# ------------------------------------------------------ PYTEST ------------------------------------------------------ #
pytestmark: MarkDecorator = pytest.mark.cli


# ==================================================================================================================== #
#                                                         TESTS                                                        #
# ==================================================================================================================== #
def test_cli_no_args(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running the cli with no args prints help to stdout and exits with code 0."""
    code, out, err = run_cli([])

    assert code == 0
    assert "usage: ugit" in out
    assert "Global options" in out
    assert err == ""


def test_cli_help_option(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running `ugit --help` prints help text and exits with code 0."""
    code, out, err = run_cli(["--help"])

    assert code == 0
    assert "usage: ugit" in out
    assert "Global options" in out
    assert err == ""


def test_cli_version_option(run_cli: Callable[[list[str]], CliResult]) -> None:
    """Running `ugit --version` prints the version and exits with code 0."""
    code, out, err = run_cli(["--version"])

    expected: str = f"ugit-diy v{__version__}\n"  # argparse adds a trailing newline
    assert code == 0
    assert out == expected
    assert err == ""

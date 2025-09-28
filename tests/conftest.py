# tests/conftest.py
"""file header, to be defined later."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
from __future__ import annotations  # (default since 3.7)

from typing import TYPE_CHECKING, NamedTuple

# 3rd party
import pytest

# Local
from ugit_diy.cli import main

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Sequence

    from _pytest.capture import CaptureResult


class CliResult(NamedTuple):
    """Result of running the CLI: (exit code, stdout, stderr)."""

    code: int
    out: str
    err: str


# ==================================================================================================================== #
#                                                       FIXTURES                                                       #
# ==================================================================================================================== #
@pytest.fixture()
def run_cli(capsys: pytest.CaptureFixture[str]):
    """Return a callable that runs the CLI with argv and returns (code, out, err).

    No global state patches or SystemExit handling needed.
    """

    def _runner(argv: Sequence[str]) -> CliResult:
        code = main(argv)
        captured: CaptureResult[str] = capsys.readouterr()
        return CliResult(code, captured.out, captured.err)

    return _runner

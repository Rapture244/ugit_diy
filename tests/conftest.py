# tests/conftest.py
"""file header, to be defined later."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
from __future__ import annotations  # (default since 3.7)

import sys
from typing import TYPE_CHECKING, NamedTuple

# 3rd party
import pytest

# Local
from ugit_diy.cli import main

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Callable

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
def run_cli(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> Callable[[list[str]], CliResult]:
    """Return a callable that runs the CLI with argv and returns (code, out, err)."""

    def _runner(argv: list[str]) -> CliResult:
        monkeypatch.setattr(sys, "argv", argv)
        exc: pytest.ExceptionInfo[SystemExit]

        with pytest.raises(SystemExit) as exc:
            main()
        captured: CaptureResult[str] = capsys.readouterr()

        # Respect argparse semantics: only int codes (or None → 0) are valid.
        code_obj = exc.value.code

        if code_obj is None:
            code = 0
        elif isinstance(code_obj, int):
            code = code_obj
        else:
            pytest.fail(f"Unexpected SystemExit code type from argparse: {type(code_obj)!r}: {code_obj}")

        return CliResult(code, captured.out, captured.err)

    return _runner

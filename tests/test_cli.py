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
from ugit_diy import __version__, cli as cli_mod
from ugit_diy.repo import RepoAlreadyExistsError

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from _pytest.mark import MarkDecorator
    from _pytest.monkeypatch import MonkeyPatch
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


def test_cli_init_success(monkeypatch: MonkeyPatch, run_cli: Callable[[list[str]], CliResult], tmp_path: Path) -> None:
    """Running `ugit init` succeeds and logs the repo path."""
    fake_repo_path: Path = tmp_path / "proj" / ".ugit"

    def _fake_init_repo() -> Path:
        return fake_repo_path

    monkeypatch.setattr(cli_mod, "init_repo", _fake_init_repo)

    code, out, err = run_cli(["init"])

    assert code == 0
    combined: str = out + err
    assert "Initialized empty ugit repository in:" in combined
    assert str(fake_repo_path) in combined


def test_cli_init_already_exists(
    monkeypatch: MonkeyPatch, run_cli: Callable[[list[str]], CliResult], tmp_path: Path
) -> None:
    """Running `ugit init` handles RepoAlreadyExistsError gracefully."""
    existing_path: Path = tmp_path / "proj" / ".ugit"

    def _raise() -> None:
        raise RepoAlreadyExistsError(existing_path)

    monkeypatch.setattr(cli_mod, "init_repo", _raise)

    code, _, err = run_cli(["init"])

    assert code == 1
    assert "Repository initialization failed: repository already exists" in err
    assert str(existing_path) in err

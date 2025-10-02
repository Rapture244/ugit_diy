# tests/test_repo.py
"""Tests for ugit_diy.repo.

This test suite checks repository initialization behavior:

- Creates the .ugit directory tree if it does not exist.
- Raises RepoAlreadyExistsError when initializing twice.
- Writes a HEAD file pointing to the default branch.
- Propagates RepoRootNotFoundError if no project root is found.
- Forwards the start_dir argument to find_repo_root().
"""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
# stdlib
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

# 3rd party
import pytest

# local
from ugit_diy.constants import UGIT_DIR
from ugit_diy.paths import RepoRootNotFoundError  # use the real exception for clarity
import ugit_diy.repo as repo

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
if TYPE_CHECKING:
    from pathlib import Path

    from _pytest.monkeypatch import MonkeyPatch


# ==================================================================================================================== #
#                                                    TEST FIXTURES                                                     #
# ==================================================================================================================== #
@pytest.fixture()
def fake_repo_root(tmp_path: Path) -> Path:
    """Create a temporary project root containing a minimal pyproject.toml.

    This simulates a valid repository root so that find_repo_root() succeeds.

    Args:
        tmp_path (Path): Pytest-provided unique temporary directory.

    Returns:
        Path: Path to the fake project root containing a pyproject.toml marker.
    """
    root: Path = tmp_path / "my_project"
    root.mkdir(parents=True, exist_ok=True)
    _ = (root / "pyproject.toml").write_text("[project]\nname='dummy'\n", encoding="utf-8")
    return root


@pytest.fixture()
def patch_find_repo_root(monkeypatch: MonkeyPatch) -> Callable[[Path, list[Path | None] | None], None]:
    """Return a helper that patches repo.find_repo_root with a stub.

    The helper installs a stub that always returns the provided Path. Optionally, it records each
    start_dir it receives into the provided list.

    Example:
        calls: list[Path | None] = []
        patch_find_repo_root(fake_root, calls)
        repo.init_repo(start_dir=some_dir)
        assert calls[-1] == some_dir

    Args:
        monkeypatch (MonkeyPatch): Fixture used to apply and auto-revert the patch.

    Returns:
        Callable[[Path, list[Path | None] | None], None]: A function that applies the patch.
    """

    def _apply(return_path: Path, calls: list[Path | None] | None = None) -> None:
        def _fake_find_repo_root(start_dir: Path | None = None) -> Path:
            if calls is not None:
                calls.append(start_dir)
            return return_path

        monkeypatch.setattr(repo, "find_repo_root", _fake_find_repo_root)

    return _apply


# ==================================================================================================================== #
#                                                         TESTS                                                        #
# ==================================================================================================================== #
def test_init_repo_creates_structure(fake_repo_root: Path, patch_find_repo_root: Callable[..., None]) -> None:
    """Ensure init_repo creates the expected .ugit layout and a valid HEAD file.

    Validates:
      - .ugit/ is created under the project root.
      - objects/, refs/heads/, and refs/tags/ subdirectories are created.
      - HEAD exists and points to refs/heads/main.

    Args:
        fake_repo_root (Path): Path to a temporary fake project root.
        patch_find_repo_root (Callable[..., None]): Fixture factory that stubs find_repo_root.
    """
    patch_find_repo_root(fake_repo_root)

    created: Path = repo.init_repo()

    assert created.exists()
    assert created.is_dir()
    assert (created / "objects").is_dir()
    assert (created / "refs" / "heads").is_dir()
    assert (created / "refs" / "tags").is_dir()

    head = created / "HEAD"
    assert head.is_file()
    assert head.read_text(encoding="utf-8") == "ref: refs/heads/main\n"


def test_init_repo_raises_if_exists(fake_repo_root: Path, patch_find_repo_root: Callable[..., None]) -> None:
    """Ensure init_repo raises RepoAlreadyExistsError if .ugit already exists.

    Args:
        fake_repo_root (Path): Path to a temporary fake project root.
        patch_find_repo_root (Callable[..., None]): Fixture factory that stubs find_repo_root.
    """
    patch_find_repo_root(fake_repo_root)

    (fake_repo_root / UGIT_DIR).mkdir(parents=True, exist_ok=True)

    with pytest.raises(repo.RepoAlreadyExistsError) as excinfo:
        _ = repo.init_repo()

    expected_path: Path = fake_repo_root / UGIT_DIR
    assert str(expected_path) in str(excinfo.value)
    assert excinfo.value.repo_path == expected_path


def test_init_repo_propagates_repo_root_not_found(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    """Verify init_repo propagates RepoRootNotFoundError from find_repo_root.

    The patch is inlined since it is used only once, keeping setup local to the test.

    Args:
        monkeypatch (MonkeyPatch): Fixture used to patch find_repo_root.
        tmp_path (Path): Path included in the raised exception for clarity.
    """

    def _raise(_start: Path | None = None) -> Path:  # type: ignore[return-type]
        """Stub find_repo_root that always raises the real exception.

        Args:
            _start (Path | None): Ignored.

        Raises:
            RepoRootNotFoundError: Simulated failure to locate a project root.
        """
        raise RepoRootNotFoundError(tmp_path)

    monkeypatch.setattr(repo, "find_repo_root", _raise)

    with pytest.raises(RepoRootNotFoundError):
        _ = repo.init_repo()


def test_init_repo_respects_start_dir(
    fake_repo_root: Path, tmp_path: Path, patch_find_repo_root: Callable[..., None]
) -> None:
    """Ensure init_repo(start_dir=...) forwards the argument to find_repo_root.

    Also checks that the repository is created under the resolved project root.

    Args:
        fake_repo_root (Path): Path to a temporary fake project root.
        tmp_path (Path): Pytest-provided unique temporary directory.
        patch_find_repo_root (Callable[..., None]): Fixture factory that stubs find_repo_root and records
            the start_dir argument.
    """
    calls: list[Path | None] = []
    patch_find_repo_root(fake_repo_root, calls=calls)

    start = tmp_path / "some" / "nested"
    start.mkdir(parents=True, exist_ok=True)

    created = repo.init_repo(start_dir=start)

    # Ensure start_dir was passed through
    assert calls
    assert calls[-1] == start

    # And repo was still created in the fake root
    assert created == fake_repo_root / UGIT_DIR

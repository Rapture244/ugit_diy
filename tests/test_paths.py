# tests/test_paths.py
"""Tests for `ugit_diy.paths`.

This module tests the repository discovery logic implemented in `find_repo_root` and the
`RepoRootNotFoundError` exception. It ensures correct behavior for valid projects, nested
subdirectories, and failure cases.
"""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
from __future__ import annotations

# stdlib
from typing import TYPE_CHECKING

# 3rd party
import pytest

# local
import ugit_diy.paths as paths

# --------------------------------------------------- BASEDPYRIGHT --------------------------------------------------- #
# Imported only for static checkers; not used at runtime.
if TYPE_CHECKING:
    from pathlib import Path

# ==================================================================================================================== #
#                                                    FIND_REPO_ROOT                                                    #
# ==================================================================================================================== #


# --------------------------------------------------- SUCCESS CASES -------------------------------------------------- #
def test_find_repo_root_returns_repo_root_when_pyproject_exists(tmp_path: Path) -> None:
    """Test that `find_repo_root` returns the correct root when `pyproject.toml` exists.

    Verifies that if a `pyproject.toml` file is present in a directory, the function correctly
    identifies that directory as the repository root.

    Args:
        tmp_path: Temporary path provided by pytest as an isolated test directory.
    """
    repo_root: Path = tmp_path / "myrepo"
    repo_root.mkdir()
    _ = (repo_root / "pyproject.toml").write_text("[project]\nname='dummy'\n", encoding="utf-8")

    found_root = paths.find_repo_root(repo_root)
    assert found_root == repo_root


def test_find_repo_root_climbs_up_to_parent_to_find_root(tmp_path: Path) -> None:
    """Test that `find_repo_root` walks upward from a subdirectory to find the root.

    Ensures the function correctly traverses parent directories when `pyproject.toml`
    is not present in the starting directory but exists higher up.

    Args:
        tmp_path: Temporary path provided by pytest as an isolated test directory.
    """
    repo_root: Path = tmp_path / "repo"
    nested_dir: Path = repo_root / "src" / "ugit_diy"
    nested_dir.mkdir(parents=True)

    _ = (repo_root / "pyproject.toml").write_text("[project]\nname='dummy'\n", encoding="utf-8")

    found_root = paths.find_repo_root(nested_dir)
    assert found_root == repo_root


# --------------------------------------------------- FAILURE CASES -------------------------------------------------- #
def test_find_repo_root_raises_if_no_pyproject(tmp_path: Path) -> None:
    """Test that `find_repo_root` raises `RepoRootNotFoundError` if no `pyproject.toml` is found.

    Verifies that the function raises the expected exception when searching upward from a directory
    tree that does not contain a `pyproject.toml`.

    Args:
        tmp_path: Temporary path provided by pytest as an isolated test directory.
    """
    orphan_dir: Path = tmp_path / "orphan" / "nested"
    orphan_dir.mkdir(parents=True)

    with pytest.raises(paths.RepoRootNotFoundError) as excinfo:
        _ = paths.find_repo_root(orphan_dir)

    # Verify the error message mentions the start directory
    start_str = str(orphan_dir.resolve())
    assert "Could not find an upward 'pyproject.toml'" in str(excinfo.value)
    assert start_str in str(excinfo.value)

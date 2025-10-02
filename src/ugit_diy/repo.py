# !INFO: src/ugit_diy/repo.py
"""TODO: Module docstring here & for the entire thing."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
from __future__ import annotations

# stdlib
from typing import TYPE_CHECKING

# 3rd party
# local
from ugit_diy.constants import UGIT_DIR
from ugit_diy.paths import find_repo_root

# --------------------------------------------------- BASEDPYRIGHT --------------------------------------------------- #
# Imported only for static checkers; not used at runtime.
if TYPE_CHECKING:
    from pathlib import Path


# ==================================================================================================================== #
#                                                   EXCEPTIONS                                                         #
# ==================================================================================================================== #
class RepoAlreadyExistsError(FileExistsError):
    """Raised when trying to initialize a repo where one already exists."""

    def __init__(self, repo_path: Path) -> None:
        """Initialize the error with the path to the existing repository.

        Args:
            repo_path: Path where a `.ugit` repository already exists.
        """
        super().__init__(f"Repository already exists at: {repo_path}")
        self.repo_path: Path = repo_path


# ==================================================================================================================== #
#                                                         REPO                                                         #
# ==================================================================================================================== #


def init_repo(start_dir: Path | None = None) -> Path:
    """Initialize a new `.ugit` repository under the project root.

    Searches upward from the given directory (or the current working directory)
    for a `pyproject.toml` to locate the project root, then creates the `.ugit`
    directory structure used by ugit.

    The created layout looks like this::

        .ugit/
        ├─ objects/
        ├─ refs/
        │  ├─ heads/
        │  └─ tags/
        └─ HEAD   (contents: "ref: refs/heads/main")

    Args:
        start_dir (Path | None): Optional starting directory. Defaults to the current working directory.

    Returns:
        Path: Absolute path to the created `.ugit` directory.

    Raises:
        RepoAlreadyExistsError: If a `.ugit` directory already exists.
        RepoRootNotFoundError: If no `pyproject.toml` is found.
    """
    root: Path = find_repo_root(start_dir)
    repo_path: Path = root / UGIT_DIR

    if repo_path.exists():
        raise RepoAlreadyExistsError(repo_path)
    # Create .ugit structure
    (repo_path / "objects").mkdir(parents=True)
    (repo_path / "refs" / "heads").mkdir(parents=True)
    (repo_path / "refs" / "tags").mkdir(parents=True)
    _ = (repo_path / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

    return repo_path

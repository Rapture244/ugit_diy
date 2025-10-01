# src/ugit_diy/paths.py
"""TODO: Add docstrings."""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
from __future__ import annotations

# stdlib
from pathlib import Path

# Local


# ==================================================================================================================== #
#                                                   EXCEPTIONS                                                         #
# ==================================================================================================================== #
class RepoRootNotFoundError(FileNotFoundError):
    """Raised when the repository root cannot be located.

    The repository root is determined by walking upward from a starting directory until a pyproject.toml file is found.
    """

    def __init__(self, start_dir: Path) -> None:
        """Initialize the error with the starting directory.

        Args:
            start_dir: Directory from which the upward search was initiated.
        """
        msg: str = (
            f"Could not find an upward 'pyproject.toml' starting from: {start_dir}. "
            f"Ensure you're running this inside a valid Python project directory."
        )
        super().__init__(msg)


# ==================================================================================================================== #
#                                                         PATHS                                                        #
# ==================================================================================================================== #


def find_repo_root(start_dir: Path | None = None) -> Path:
    """Return the absolute path to the repository root directory.

    Searches upward from the given directory (or the current working directory if not provided) until a pyproject.toml
    file is found. The directory containing that file is returned.

    Args:
        start_dir: Optional starting directory. Defaults to the current working directory.

    Returns:
        Path: Absolute path to the repository root directory.

    Raises:
        RepoRootNotFoundError: If no pyproject.toml is found in the starting directory or any of its parents.
    """
    start_abs_path: Path = (start_dir or Path.cwd()).resolve()
    for candidate in [start_abs_path, *start_abs_path.parents]:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RepoRootNotFoundError(start_abs_path)

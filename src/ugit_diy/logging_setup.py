# src/ugit_diy/logging_setup.py
"""Logging setup utilities for ugit_diy.

Runtime behavior:
    1) Load the packaged logging dictConfig JSON referenced by LOGGING_CONFIG_RESOURCE_PATH.
    2) Normalize any file-handler filename into <REPO_ROOT>/logs (basename only).
    3) Apply dictConfig. If UGIT_LOG_LEVEL is set, override the root level accordingly.
    4) If packaged config can't be loaded or applied, fall back to logging.basicConfig with an ISO-ish format.

Design choices:
    - Configure once, then emit any boot warnings (so log capture works predictably).
    - Validate LOGGING_CONFIG_RESOURCE_PATH at import time and hard-fail fast if it's malformed.
    - No support for an external env-provided JSON path; this CLI ships its own logging config.

Environment Variables:
    UGIT_LOG_LEVEL:
        Optional override applied after dictConfig. Accepts the standard level names:
        DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
from __future__ import annotations

# stdlib
from collections.abc import MutableMapping
from functools import lru_cache
from importlib.resources import files as resources_files
import json
import logging
import logging.config
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

# Local
from ugit_diy.constants import LOGGING_CONFIG_RESOURCE_PATH
from ugit_diy.paths import find_repo_root

# --------------------------------------------------- BASEDPYRIGHT --------------------------------------------------- #
# Imported only for static checkers; not used at runtime.
if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

# ==================================================================================================================== #
#                                                   EXCEPTIONS                                                         #
# ==================================================================================================================== #


class InvalidLoggingConfigPathError(ValueError):
    """Raised when LOGGING_CONFIG_RESOURCE_PATH is malformed.

    The LOGGING_CONFIG_RESOURCE_PATH constant must be a 3-item tuple of non-empty strings:
    (package, subdir, filename).
    """

    def __init__(self) -> None:
        """Initialize with a descriptive validation message."""
        super().__init__("LOGGING_CONFIG_RESOURCE_PATH must be a 3-item tuple of strings: (package, subdir, filename)")


# ==================================================================================================================== #
#                                                       CONSTANTS                                                      #
# ==================================================================================================================== #
# Hard-validate LOGGING_CONFIG_RESOURCE_PATH at import time (fail fast, explicit error).
try:
    _PKG, _SUBDIR, _FILENAME = LOGGING_CONFIG_RESOURCE_PATH
except Exception as exc:  # shape/type issues
    raise InvalidLoggingConfigPathError from exc

if not all(x for x in (_PKG, _SUBDIR, _FILENAME)):
    raise InvalidLoggingConfigPathError


# ------------------------------------ ENVIRONMENT VARIABLES (OPTIONAL OVERRIDES) ------------------------------------ #
# Single optional override: root level bump after dictConfig
ENV_LOG_LEVEL: str = "UGIT_LOG_LEVEL"  # DEBUG/INFO/WARNING/ERROR/CRITICAL

# ==================================================================================================================== #
#                                                 INTERNAL PATH HELPERS                                                #
# ==================================================================================================================== #


@lru_cache(maxsize=1)
def _ensure_repo_logs_dir() -> Path:
    """Ensure and return the logs directory path.

    Resolves the repository root using ``find_repo_root()`` and ensures a ``logs`` directory
    exists at its top level. The directory is created if it does not already exist.

    Returns:
        Path: Absolute path to the ``logs`` directory within the repository root.
    """
    repo_root: Path = find_repo_root(Path(__file__).parent)
    logs_dir: Path = repo_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


# ==================================================================================================================== #
#                                                 CONFIG NORMALIZATION                                                 #
# ==================================================================================================================== #


def _apply_repo_local_filename(config: MutableMapping[str, object], logs_dir: Path) -> None:
    """Rewrite file-handler filename paths to reside under logs_dir.

    Only the basename of each configured filename is preserved; the directory component is replaced
    by logs_dir. This applies only to handlers that appear to be file-based (class name containing
    'FileHandler') and that expose a filename field in the dictConfig.

    Args:
        config: Logging configuration dictionary (PEP 282 / dictConfig format). Modified in place.
        logs_dir: Target directory for file-based handler outputs.
    """
    handlers_section: object = config.get("handlers", {})
    if not isinstance(handlers_section, MutableMapping):
        return

    handlers_map: MutableMapping[str, object] = cast("MutableMapping[str, object]", handlers_section)

    for handler_cfg_obj in handlers_map.values():
        if not isinstance(handler_cfg_obj, MutableMapping):
            continue

        handler_cfg: MutableMapping[str, object] = cast("MutableMapping[str, object]", handler_cfg_obj)
        # Guard: only handle classes that look like file handlers and expose a 'filename'
        handler_class_name: str = str(handler_cfg.get("class", ""))

        # matches FileHandler / RotatingFileHandler / TimedRotating...
        looks_like_file_handler: bool = "FileHandler" in handler_class_name

        if looks_like_file_handler and "filename" in handler_cfg:
            filename_value: object = handler_cfg.get("filename", "")
            filename_basename: str = Path(str(filename_value)).name
            handler_cfg["filename"] = str(logs_dir / filename_basename)


# ==================================================================================================================== #
#                                                  CONFIG LOADING LOGIC                                                #
# ==================================================================================================================== #


def _load_packaged_logging_json() -> dict[str, object] | None:
    """Load the packaged logging configuration JSON, if available.

    The function expects LOGGING_CONFIG_RESOURCE_PATH to be a tuple (package, subdir, filename).
    It resolves that resource using importlib.resources, reads its contents as UTF-8, and parses
    the result as JSON.

    Returns:
        The parsed dictConfig mapping if found and valid; otherwise None.
    """
    try:
        resource_path: Traversable = resources_files(_PKG) / _SUBDIR / _FILENAME
        if not resource_path.is_file():
            return None
        text: str = resource_path.read_text(encoding="utf-8")
        return cast("dict[str, object]", json.loads(text))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


# ==================================================================================================================== #
#                                             INTERNAL CONFIGURE/EMIT HELPERS                                          #
# ==================================================================================================================== #


def _configure_fallback() -> None:
    """Install a minimal fallback logging configuration and enable warnings capture.

    The fallback uses logging.basicConfig with an ISO-like timestamp format. The effective level is
    taken from UGIT_LOG_LEVEL when set (defaults to INFO).
    """
    level_name = os.environ.get(ENV_LOG_LEVEL, "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | [%(threadName)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        force=True,
    )
    logging.captureWarnings(True)


def _emit_warnings_now(warnings_to_emit: list[tuple[str, tuple[object, ...]]]) -> None:
    """Emit queued warnings using this module's logger.

    This is called only after at least one handler has been installed, to ensure messages are visible
    and testable.

    Args:
        warnings_to_emit: Sequence of (message, args) tuples compatible with logger.warning.
    """
    logger = logging.getLogger(__name__)
    for msg, args in warnings_to_emit:
        logger.warning(msg, *args)


# ==================================================================================================================== #
#                                                   PUBLIC API: SETUP                                                  #
# ==================================================================================================================== #


def setup_logging() -> None:
    """Configure project-wide logging using packaged defaults; fall back to basicConfig if needed.

    Steps:
        - Load packaged dictConfig JSON.
        - Rewrite file handler paths into <REPO_ROOT>/logs.
        - Apply dictConfig.
        - Optionally apply UGIT_LOG_LEVEL to the root logger.
        - If anything fails, install a basic fallback and warn.

    Notes:
        We queue up any boot warnings and emit them only after a handler exists, for reliable capture.
    """
    logs_dir: Path = _ensure_repo_logs_dir()
    boot_warnings: list[tuple[str, tuple[object, ...]]] = []

    config = _load_packaged_logging_json()
    if config is None:
        boot_warnings.append(("Packaged logging.json dictConfig not found or invalid, falling back.", ()))
        _configure_fallback()
        _emit_warnings_now(boot_warnings)
        return

    try:
        _apply_repo_local_filename(cast("MutableMapping[str, object]", config), logs_dir)
        logging.config.dictConfig(config)
        logging.captureWarnings(True)

        # Optional root-level override
        env_root_level = os.environ.get(ENV_LOG_LEVEL)
        if env_root_level:
            lvl: int | None = getattr(logging, env_root_level.upper(), None)
            if isinstance(lvl, int):
                logging.getLogger().setLevel(lvl)

    except Exception:
        _configure_fallback()
        # ensure users see the underlying configuration failure
        logging.getLogger(__name__).exception("Invalid packaged logging configuration; using basicConfig.")
    finally:
        _emit_warnings_now(boot_warnings)

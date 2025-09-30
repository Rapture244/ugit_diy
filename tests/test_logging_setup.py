# tests/test_logging_setup.py
"""Tests for `ugit_diy.logging_setup`.

This module tests the logging setup behavior of the `ugit_diy` package. It validates:

- Path normalization for file-based logging handlers.
- Fallback behavior when the packaged logging configuration is missing or invalid.
- Correct handling of the `UGIT_LOG_LEVEL` environment variable in fallback and packaged modes.
- Proper rewriting of file handler paths into `<REPO_ROOT>/logs`.
- Utility behavior of `get_logs_dir()` ensuring the log directory exists.

These tests ensure the logging configuration is applied predictably and robustly across different scenarios.
"""

# ==================================================================================================================== #
#                                                        IMPORTS                                                       #
# ==================================================================================================================== #
from __future__ import annotations

# stdlib
from collections.abc import MutableMapping
import logging
from pathlib import Path
from typing import TYPE_CHECKING, cast

# 3rd party
import pytest

# local
import ugit_diy.logging_setup as logsetup  # import the module and call functions off it

# ------------------------------------------------------ PYRIGHT ----------------------------------------------------- #
# Type-only imports (kept out of runtime for speed/cleanliness).
if TYPE_CHECKING:
    from collections.abc import Iterator

    from _pytest.capture import CaptureFixture


# ==================================================================================================================== #
#                                                     TEST FIXTURES                                                    #
# ==================================================================================================================== #
@pytest.fixture(autouse=True)
def _reset_logging_state() -> Iterator[None]:  # pyright: ignore[reportUnusedFunction]
    """Reset the global logging state before and after each test.

    This ensures that previous tests do not leak logging configuration into subsequent ones.
    It clears all handlers, resets the root logger level, and disables warnings capture.
    """
    # Before
    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()
    root_logger.setLevel(logging.NOTSET)
    logging.captureWarnings(False)
    yield
    # After
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()
    root_logger.setLevel(logging.NOTSET)
    logging.captureWarnings(False)


@pytest.fixture()
def tmp_logs_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide an isolated `<REPO_ROOT>/logs` directory by faking repo discovery.

    This fixture replaces `_discover_repo_root()` so that functions using it will resolve a temporary
    project structure instead of the real one.

    Args:
        tmp_path: A pytest-provided temporary directory unique per test.
        monkeypatch: Fixture to safely patch functions or environment variables.

    Returns:
        Path: Absolute path to the fake `<REPO_ROOT>/logs` directory.
    """
    fake_repo_root: Path = tmp_path / "repo"
    logs_directory: Path = fake_repo_root / "logs"

    # Ensure the fake repo directory exists before writing pyproject.toml
    fake_repo_root.mkdir(parents=True, exist_ok=True)
    _ = (fake_repo_root / "pyproject.toml").write_text("[project]\nname='dummy'\n", encoding="utf-8")

    def _fake_discover_repo_root(_start: Path) -> Path:
        return fake_repo_root

    monkeypatch.setattr(logsetup, "_discover_repo_root", _fake_discover_repo_root)
    # Clear lru_cache for _ensure_repo_logs_dir since we stub its dependency
    logsetup._ensure_repo_logs_dir.cache_clear()  # pyright: ignore[reportPrivateUsage]
    return logs_directory


# ==================================================================================================================== #
#                                           UNIT: HANDLER PATH NORMALIZATION                                           #
# ==================================================================================================================== #


def test_apply_repo_local_filename_basename_only(tmp_path: Path) -> None:
    """Test that `_apply_repo_local_filename` rewrites only basenames into `logs_dir`.

    Verifies that:
      - File handler `filename` values are rewritten to `<logs_dir>/<basename>`.
      - Non-file handlers are ignored.
    """
    logs_directory: Path = tmp_path / "logs"
    logs_directory.mkdir(parents=True, exist_ok=True)

    dict_config: dict[str, object] = {
        "version": 1,
        "handlers": {
            "file1": {"class": "logging.FileHandler", "filename": "/var/log/myapp/app.log"},
            "file2": {"class": "logging.handlers.RotatingFileHandler", "filename": "nested/other.log"},
            "console": {"class": "logging.StreamHandler"},  # Should be ignored
        },
    }

    logsetup._apply_repo_local_filename(  # pyright: ignore[reportPrivateUsage]
        cast("MutableMapping[str, object]", dict_config),
        logs_directory,
    )

    handlers_config = cast("MutableMapping[str, MutableMapping[str, object]]", dict_config["handlers"])
    assert Path(str(handlers_config["file1"]["filename"])) == logs_directory / "app.log"
    assert Path(str(handlers_config["file2"]["filename"])) == logs_directory / "other.log"
    assert "filename" not in handlers_config["console"]


# ==================================================================================================================== #
#                                 SETUP: FALLBACK CONFIGURATION (NO PACKAGED JSON)                                     #
# ==================================================================================================================== #


def test_setup_logging_fallback_when_packaged_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    """Test that `setup_logging` falls back to `basicConfig` when no packaged config exists.

    Verifies that:
      - Root logger defaults to `INFO` level.
      - A warning message is emitted to `stderr` about fallback mode.

    Args:
        monkeypatch: Used to simulate missing packaged config.
        capsys: Captures `stderr` output from the logging system.
    """
    monkeypatch.delenv(logsetup.ENV_LOG_LEVEL, raising=False)
    monkeypatch.setattr(logsetup, "_load_packaged_logging_json", lambda: None)

    # Do NOT use caplog here; basicConfig(force=True) will remove its handler.
    logsetup.setup_logging()

    # Root level is INFO by default in fallback
    root_logger = logging.getLogger()
    assert root_logger.getEffectiveLevel() == logging.INFO

    # Warning emitted to stderr by the fallback StreamHandler
    captured = capsys.readouterr()
    assert "Packaged logging.json dictConfig not found or invalid, falling back." in captured.err


def test_setup_logging_fallback_respects_env_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that fallback configuration honors `UGIT_LOG_LEVEL`.

    Args:
        monkeypatch: Used to set the `UGIT_LOG_LEVEL` environment variable.
    """
    monkeypatch.setattr(logsetup, "_load_packaged_logging_json", lambda: None)
    monkeypatch.setenv(logsetup.ENV_LOG_LEVEL, "WARNING")

    logsetup.setup_logging()

    assert logging.getLogger().getEffectiveLevel() == logging.WARNING


# ==================================================================================================================== #
#                              SETUP: PACKAGED CONFIGURATION & FILE PATH REWRITE                                       #
# ==================================================================================================================== #


def test_setup_logging_applies_packaged_and_rewrites_paths(tmp_logs_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that packaged `dictConfig` is applied and file paths are rewritten correctly.

    Verifies that:
      - File handler paths are rewritten into `<REPO_ROOT>/logs`.
      - Log files are actually created when writing logs.

    Args:
        tmp_logs_dir: Temporary `<REPO_ROOT>/logs` directory.
        monkeypatch: Used to inject a fake packaged logging configuration.
    """
    dict_config = {
        "version": 1,
        "formatters": {"fmt": {"format": "%(levelname)s %(message)s"}},
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "level": "INFO",
                "formatter": "fmt",
                "filename": "any/relative/path/app.log",
            },
        },
        "root": {"level": "INFO", "handlers": ["file"]},
    }

    _ = tmp_logs_dir  # ensure repo/logs is set up by fixture
    monkeypatch.setattr(logsetup, "_load_packaged_logging_json", lambda: dict_config)

    # Act
    logsetup.setup_logging()
    logging.getLogger("test").info("Hello file")

    # Assert the file handler writes into <repo>/logs with the basename only
    root_logger = logging.getLogger()
    installed_file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
    assert installed_file_handlers, "Expected a FileHandler to be installed by dictConfig."

    file_handler = installed_file_handlers[0]
    log_file_path = Path(file_handler.baseFilename)
    assert log_file_path.parent == tmp_logs_dir
    assert log_file_path.name == "app.log"
    assert log_file_path.exists(), "Log file should exist after an info() call."


def test_setup_logging_packaged_level_override_with_env(tmp_logs_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that `UGIT_LOG_LEVEL` overrides the root logger level even with packaged config.

    Args:
        tmp_logs_dir: Temporary `<REPO_ROOT>/logs` directory.
        monkeypatch: Used to inject a fake packaged logging configuration and set the env var.
    """
    dict_config = {
        "version": 1,
        "handlers": {"null": {"class": "logging.NullHandler"}},
        "root": {"level": "INFO", "handlers": ["null"]},
    }

    _ = tmp_logs_dir
    monkeypatch.setattr(logsetup, "_load_packaged_logging_json", lambda: dict_config)
    monkeypatch.setenv(logsetup.ENV_LOG_LEVEL, "ERROR")

    logsetup.setup_logging()

    assert logging.getLogger().getEffectiveLevel() == logging.ERROR


# ==================================================================================================================== #
#                                         UTILITY: REPO LOG DIRECTORY CREATION                                         #
# ==================================================================================================================== #


def test_get_logs_dir_creates_and_returns_repo_logs(tmp_logs_dir: Path) -> None:
    """Test that `get_logs_dir()` returns and creates `<REPO_ROOT>/logs` if necessary.

    Args:
        tmp_logs_dir: Temporary `<REPO_ROOT>/logs` directory.
    """
    logs_directory = logsetup.get_logs_dir()
    assert logs_directory == tmp_logs_dir
    assert logs_directory.exists()
    assert logs_directory.is_dir()

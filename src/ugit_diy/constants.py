# src/ugit_diy/constants.py
"""This is a docstring."""

# ------------------------------------------- DISTRIBUTION/PACKAGE METADATA ------------------------------------------ #
# IMPORTANT: Must match the `[project].name` field in pyproject.toml.
DIST_NAME = "ugit-diy"

# -------------------------------------------------- LOGGING --------------------------------------------------------- #
# Default packaged logging configuration (relative to the package)
LOGGING_CONFIG_RESOURCE_PATH: tuple[str, ...] = ("ugit_diy", "config", "logging.json")

# -------------------------------------------------------- CLI ------------------------------------------------------- #
# (Reserved for future CLI-related constants, e.g., default command names or paths)
# CLI_DEFAULT_COMMAND = "status"


# -------------------------------------------------------- GIT ------------------------------------------------------- #
# (Reserved for git-related constants, e.g., default branch or refs)
# GIT_DEFAULT_BRANCH = "main"


# -------------------------------------------------------- PATHS ----------------------------------------------------- #
# (Reserved for paths you might need project-wide, e.g., cache or data directories)
# PATHS_DEFAULT_CACHE_DIR = "cache"

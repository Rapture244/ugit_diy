# 🪵 Logging

## 📖 Core logging concepts: levels, loggers, and handlers

Before diving into the module itself, it’s worth understanding two key ideas that shape how logging is configured and behaves in Python: **numeric log levels** and **logger hierarchy**.

1. **Numeric log levels — what, why, when**  
   - Every log level has a **name** and a **numeric value**:  
     `CRITICAL=50`, `ERROR=40`, `WARNING=30`, `INFO=20`, `DEBUG=10`, `NOTSET=0`.  
   - Internally, Python uses the **numeric values** to decide whether to emit a record (“log or drop?”).  
   - Numeric levels become useful when:
     - Writing **structured logs** (e.g., JSON) for better filtering and thresholding in tools.
     - Aggregating logs and computing metrics (e.g., “% of ERROR+ over time”).
     - Implementing custom filters (e.g., “drop anything `< 25`”).
     - In human-readable logs, you don’t typically display the numeric level. But in structured logs, including a `levelno` field is best practice.  
     👉 TL;DR — Keep your text formatters as-is. If you adopt JSON logs later, add `levelno` to the object.

2. **Root logger vs package loggers — handler strategy**  
   - A clean and scalable setup is a **hybrid model**:
     - Set the **root logger** to `WARNING` to silence most 3rd-party noise.
     - Set your **package logger** (e.g., `ugit_diy`) to `DEBUG` with `propagate=True` and **no handlers**.
     - Attach handlers only to the **root logger**.
   - Result:
     - Console output stays clean (shows INFO+ from your package).
     - Full detail is still captured in log files.
     - 3rd-party libraries remain quiet unless they log WARNING+.

---

## 📦 Module overview: `logging_setup.py`

This module is the **centralized logging bootstrap** for the whole project. Its job is to ensure logging is configured consistently, predictably, and safely across all environments — whether you’re running the CLI, tests, or library code.

Here are the big ideas behind its design and behavior:

1. **One source of truth: packaged `dictConfig`**  
   - A structured JSON config file ships **inside the package**.  
   - At startup, the module **loads and applies that config** with `logging.config.dictConfig`.  
   - It **never accepts external paths from the environment**, preventing config drift and ensuring reproducibility.

2. **Normalize all file outputs to `<REPO_ROOT>/logs`**  
   - Any file-based handler is rewritten so it logs into a `logs/` directory **under the repository root** (found by walking upward until `pyproject.toml` is discovered).  
   - Only the **basename** is preserved.  
   - This guarantees logs always end up in a predictable place, regardless of what the packaged config said.

3. **Environment-level override: `UGIT_LOG_LEVEL`**  
   - Even if the dictConfig defines levels, the **root logger** can be bumped globally via `UGIT_LOG_LEVEL`.  
   - Applied *after* config load, it acts as a final override — ideal for debugging or CI without touching config files.

4. **Fail fast, fail safe**  
   - The resource path tuple is validated at import time. If malformed, it raises immediately.  
   - If the packaged config is missing or invalid, it **falls back** to a minimal `basicConfig` setup with an ISO-style timestamp.  
   - A warning is logged, but the process never crashes — logging must never silently fail.

5. **Emit boot warnings *after* handlers exist**  
   - Any warnings gathered during setup are emitted **only after** a handler is configured.  
   - This ensures they’re properly logged and visible in your logs and tests.

---

## 🧪 Pytest overview

Tests for `ugit_diy.logging_setup` validate that logging behaves predictably and robustly across all scenarios — missing configs, environment overrides, fake repos, etc. They aim to ensure logging is **reliable, isolated, and reproducible**.

1. **Global state isolation**  
   - `_reset_logging_state` fixture clears handlers, resets the root logger, and disables warnings capture before and after each test.  
   - Prevents state leakage between tests, which is crucial because logging is global.

2. **Fake repo roots for predictable paths**  
   - `tmp_logs_dir` fixture creates a temporary fake repo with a `pyproject.toml`, patches `_discover_repo_root()` to return it, clears `_ensure_repo_logs_dir`’s cache, and returns `<repo>/logs`.  
   - This allows deterministic verification of path rewriting logic.

3. **Handler path normalization**  
   - `test_apply_repo_local_filename_basename_only` checks that `_apply_repo_local_filename` rewrites all file-handler paths into `<logs_dir>/<basename>` while ignoring non-file handlers.

4. **Fallback behavior**  
   - `test_setup_logging_fallback_when_packaged_missing` ensures the module falls back to `basicConfig` when no packaged config exists, sets the root logger to `INFO`, and emits a warning.  
   - `test_setup_logging_fallback_respects_env_level` verifies that `UGIT_LOG_LEVEL` still overrides the root level even in fallback mode.

5. **Packaged configuration and path rewrite**  
   - `test_setup_logging_applies_packaged_and_rewrites_paths` confirms that packaged `dictConfig` is applied, file paths are normalized into `<REPO_ROOT>/logs`, and log files are created.  
   - `test_setup_logging_packaged_level_override_with_env` verifies that `UGIT_LOG_LEVEL` overrides the root logger level even when a packaged config is present.

6. **Utility behavior**  
   - `test_get_logs_dir_creates_and_returns_repo_logs` checks that `get_logs_dir()` returns the canonical logs directory, ensures it exists, and matches the expected path.

---

# References 
- [Python - Logging module docs](https://docs.python.org/3.12/library/logging.html)  
- [mCoding: Modern Python logging (YouTube)](https://youtu.be/9L77QExPmI0?si=w_IAnAioyhNx4tbE)

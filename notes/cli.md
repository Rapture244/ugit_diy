# 🧰 CLI Design Notes

## 📦 Overview

The `ugit` command-line interface is a **minimal, scalable, and testable CLI** designed to grow into a full Git-like tool.  
Its current responsibilities:

- Provide global options (`--help`, `--version`).
- Print concise help text when invoked with no arguments.
- Exit predictably with meaningful return codes.

The CLI is deliberately **simple, explicit, and structured** — every design choice aims to make it easy to extend (`ugit init`, `ugit log`, etc.) without refactoring the core.

---

## 🧭 Core Design Principles

- 🧱 **Layered architecture** &xrarr; Parser construction, command dispatch, and process entry are separate and composable.
- 🧪 **Testability by design** &xrarr; Pure function entrypoint (`main(argv) -> int`) with no reliance on global state.
- 🧰 **Standard-library first** &xrarr; Uses `argparse` to master fundamentals before considering frameworks like Typer or Click.
- 🔁 **Future-ready** &xrarr; New subcommands plug into `_build_parser()` and `_dispatch()` without breaking existing behavior.
- 📏 **Predictable exit codes** &xrarr; All `SystemExit` signals from `argparse` are normalized into integer return codes.

---

## 🏗️ CLI Components

| File              | Role                                                                                                          |
|-------------------|---------------------------------------------------------------------------------------------------------------|
| **`cli.py`**      | Core of the CLI. Builds the parser, defines global flags, handles no-arg behavior, and dispatches commands.   |
| **`conftest.py`** | Provides a `run_cli()` fixture to execute the CLI with arbitrary arguments and capture outputs.               |
| **`test_cli.py`** | Validates core behaviors (`ugit`, `--help`, `--version`) and provides a template for testing future commands. |

--- 


## 🧩 Subcommands (Planned)

- `ugit` — base command (prints help if no args)
- Global options:
  - `-h, --help` — show help
  - `-v, --version` — show version info

Future subcommands will follow the pattern:

- `ugit init` — initialize a repository  
- `ugit log` — view commit history  
- `ugit commit` — commit staged changes

Each subcommand will be handled centrally by `_dispatch()`.

---

## 🏗️ CLI Architecture

The CLI follows a **three-layer design** for clarity and growth:

1. Parser Construction &xrarr; `_build_parser()`
   - Declares all global flags (`--help`, `--version`).
   - Controls output formatting (e.g. `ArgumentDefaultsHelpFormatter`).
   - Disables abbreviation (`allow_abbrev=False`) to avoid accidental matches.
   - Uses standard `help` and `version` actions — no custom handling required.

📌 **Note:** The version string prefers installed distribution metadata (`importlib.metadata.version()`), falling back to `__version__` in development.

2. Core Logic &xrarr; `main(argv) -> int`
   - Accepts `argv` explicitly for testability. Falls back to `sys.argv[1:]` when run normally.
   - Configures logging **early** by calling `setup_logging()` from `logging_setup.py`, ensuring logs are captured even during argument parsing.
   - If no arguments are provided &xrarr; prints help and exits `0`.
   - Catches `SystemExit` from `argparse` and converts it into an integer return code.

This makes `main()` a **pure function**: input is `argv`, output is an exit code — no global state, no implicit side effects.

3. Dispatch Layer &xrarr; `_dispatch(ns)`
   - Responsible for routing parsed arguments (`Namespace`) to the correct command handler.
   - Currently returns `0` because no subcommands are implemented yet.
   - Future commands will branch here (e.g., `if ns.cmd == "init": return do_init()`).

4. Process Entry &xrarr; `if __name__ == "__main__"`
   - Thin wrapper around `main()` that calls `sys.exit(main(sys.argv[1:]))`.
   - Keeps runtime execution separate from core logic, which is crucial for testability.

--- 

## 🧠 Core Concepts and Patterns

- ✅ **Explicit `argv` input** — `main(argv)` avoids reliance on global `sys.argv`, improving predictability and testability.
- 🧪 **Graceful `SystemExit` handling** — All `argparse` exits (help/version/parse errors) become integer codes:
  - `--help` &xrarr; prints help, exits `0`
  - `--version` &xrarr; prints version, exits `0`
  - invalid args &xrarr; prints usage to `stderr`, exits `2`
- 🪶 **Separation of concerns** — `_build_parser()` defines structure, `main()` orchestrates flow, `_dispatch()` executes behavior.
- 🔌 **Future-proof dispatch** — Adding new subcommands is additive, not disruptive.
- 📊 **Logging-first design** — Early call to `setup_logging()` integrates the CLI with the centralized logging strategy.


---

## 🧪 Pytest Overview

The test suite validates that the CLI behaves predictably in all current scenarios and is ready for future commands:

### Fixtures

- **`run_cli()`** — Runs `main(argv)` and captures `(exit_code, stdout, stderr)` with `capsys`.  
  &xrarr; Avoids `SystemExit` handling in tests and keeps the test surface minimal.

### Core Tests

| Test                      | Purpose                                                |
|---------------------------|--------------------------------------------------------|
| `test_cli_no_args`        | Running `ugit` with no args prints help and exits `0`. |
| `test_cli_help_option`    | `ugit --help` prints help text and exits `0`.          |
| `test_cli_version_option` | `ugit --version` prints version info and exits `0`.    |

✅ All tests assert clean `stdout`/`stderr` behavior and integer exit codes.


---

## 📚 Glossary

- **Parser** &xrarr; Defines CLI shape (flags, commands) and turns raw args into a structured `Namespace`.
- **SystemExit** &xrarr; Exception raised by `argparse` to stop execution with a specific exit code.
- **stdout / stderr** &xrarr; Standard output vs error output. Tests capture and assert on both.
- **`argv` vs `sys.argv`** &xrarr; `argv` is passed explicitly to `main()` (clean, testable); `sys.argv` is global and mutable.

---

## 🌱 Future Ideas / To Do

- Implement a basic `ugit init` subcommand to validate `_dispatch()` flow.
- Add subparsers and argument groups for nested commands (`ugit branch create`, etc.).
- Explore migration to Typer or Click — existing API (`main(argv) -> int`) will remain stable.
- Add rich terminal output and integrated logging output for better UX.

---

## ✨ Why This Design Matters

- 🔌 **Composable** — Adding new commands is trivial: define subparser, handle it in `_dispatch()`.
- 🧪 **Testable** — Pure functional entrypoint and fixture-driven tests scale with complexity.
- 🧱 **Stable foundation** — Future refactors or framework migrations won’t break the external interface.
- 📈 **Production-ready** — Clean logging integration, predictable exit codes, and robust testing practices ensure the CLI scales from “toy” to “tool.”

---

# References
- [Python `argparse` documentation](https://docs.python.org/3/library/argparse.html)
- [Hynek Schlawack – Writing CLIs with argparse (PyCon talk)](https://youtu.be/pXhcPJK5cMc)
- [Click vs Typer design notes](https://click.palletsprojects.com/)


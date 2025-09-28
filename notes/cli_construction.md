# CLI Design Notes

## 📦 Overview
A minimal, scalable command-line interface for `ugit`. It currently supports global options (`--help`, `--version`) and prints help when invoked with no arguments.  
The design is explicit, testable, and future-proof — ready to grow into a full Git-like CLI without major refactors.

---

## 🧩 Subcommands (planned)

- `ugit` — base command (prints help if no args)
- `-h, --help` — concise help text
- `-v, --version` — display version info

---

## 🧭 Core Design Principles

- 🧰 **Start with `argparse`** → Use the standard library to understand core CLI mechanics before moving to Typer or Click.
- 🧱 **Layered architecture** → Parser construction, core logic, and process execution are separated, keeping responsibilities clear and growth easy.
- 🧪 **Testability by design** → Explicit `argv` input and integer return codes make the CLI a pure function: no global state, no side effects.
- 🔁 **Future-ready structure** → Subcommands plug directly into `_build_parser()` and `_dispatch()` without breaking existing behavior.
- 📁 **Composable commands** → Each command (including global options) is implemented as its own callable, simplifying extension and refactoring.

---

## 🏗️ CLI Components

- **`cli.py`** → Builds the CLI: constructs the parser, defines global flags, handles “no-arg” behavior, and organizes future subcommands. It’s the core of the interface.
- **`conftest.py`** → Provides a reusable fixture to run the CLI with arbitrary args, capture `stdout`/`stderr`, and return structured results for tests.
- **`test_cli.py`** → Validates the CLI’s core behaviors (`ugit`, `--help`, `--version`) and serves as a template for testing future commands.

---

## 🏗️ CLI Architecture

The CLI follows a simple three-layer model:

1. **Parser Construction** → `_build_parser()`  
   Purely declarative: defines global flags, help/version actions, usage text, and formatting.

2. **Core Logic** → `main(argv) -> int`  
   Parses arguments, converts `SystemExit` into return codes, and delegates execution to subcommands.

3. **Execution Layer** → `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`  
   Thin process-facing entry point: reads `sys.argv` and exits with the return code from `main()`.

This separation **decouples CLI logic from the runtime environment**. Tests call `main([...])` directly with no global state, while real users still interact with the standard `ugit` command.

---

## 🧠 Core Design Concepts

- **Explicit `argv` input** → Arguments are passed directly into `main()` instead of reading `sys.argv`, eliminating global state and improving predictability and testability.
- **Graceful `SystemExit` handling** → `main()` catches and normalizes exit codes so tests can assert integers instead of exceptions.  
  `argparse` uses `SystemExit` for:
  - `--help` → prints help (`stdout`), exits `0`
  - `--version` → prints version (`stdout`), exits `0`
  - parse error → prints usage (`stderr`), exits `2`
- **Separation of Concerns**  
  - `_build_parser()` declares the interface  
  - `main()` coordinates parsing and flow  
  - `_dispatch()` (stub) will route to subcommands  
  - `__main__` handles process exit
- **Future-Proof Subcommands** → Adding new commands won’t require refactoring. You’ll only define a new subparser and handle it in `_dispatch()`.
- **Idiomatic `argparse` usage**  
  - Built-in `help` and `version` actions (no custom logic)
  - `allow_abbrev=False` → avoids accidental short flags
  - `ArgumentDefaultsHelpFormatter` → keeps help text self-documenting
  - Argument groups → readable, organized help output
- **Cleaner testing surface**  
  - `main(argv)` returns an `int` — no more `pytest.raises(SystemExit)`  
  - Tests pass arguments directly (`run_cli(["--help"])`)  
  - Output is captured cleanly with `capsys`

---

## 🌱 Why This Matters for Future Growth

- **Subcommands are trivial to add.** → Just declare them in `_build_parser()` and dispatch them in `_dispatch()`.  
  Example:  
  - `ugit init` → `ns.cmd == "init"` → `do_init()`  
  - `ugit log` → `ns.cmd == "log"` → `do_log()`
- **Tests scale naturally.** → The same `run_cli()` fixture works for all commands without modification.
- **No refactoring debt.** → The design choices (pure function entry, explicit `argv`, clear layers) mean the CLI can grow without rework.
- **Easy migration to modern frameworks.** → Because the external API (`main(argv) -> int`) is already clean, switching to Typer or Click later won’t break tests or entry points.

---

## 📚 Glossary

- **Parser** → Defines the shape of the CLI: flags, subcommands, and help text. It turns raw args into a structured `Namespace`.
- **SystemExit** → An exception used to stop execution with a specific exit code. `argparse` raises it for help, version, and errors.
- **stdout / stderr** → Standard output (normal program text) and error output (usage errors). Tests often capture both.
- **`argv` vs `sys.argv`** → `argv` is explicitly passed to `main()` (clean, testable). `sys.argv` is a global set by the interpreter (mutable, side effects).

---

## 🚀 Future Ideas / To Do

- Implement a simple `ugit init` subcommand to test the `_dispatch()` workflow.
- Experiment with subparsers and argument groups for nested commands.
- Explore migration to a higher-level library (e.g., Typer) without changing the external interface.
- Add richer terminal output (e.g., logging, rich formatting) to improve user experience.

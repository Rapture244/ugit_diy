# 🧰 `argparse` — Concepts I Actually Use

A concise, code-free reference to how `argparse` shapes this project’s CLI — focused on **concepts**, not APIs.

---

## ❓ Why `argparse`

- ✅ **Built-in** — zero dependencies, predictable behavior.
- 📜 **Declarative** — define the interface (flags, help, subcommands); let argparse handle UX.
- 🧱 **Mature defaults** — standardized help text, exit codes, and error handling out of the box.

---

## 🧠 Core Mental Model

- **Parser** → Declares the *shape* of the CLI — what inputs exist and how they’re presented.
- **Actions** → Built-in behaviors for flags like `--help` or `--version` that print and exit automatically.
- **Namespace** → The parsed, structured object that tells you *what the user asked for*.
- **Exit path** → The CLI returns an integer exit code; users see text on `stdout`/`stderr`.

---

## 📦 Top-Level Parser Essentials

- **`prog`** → Program name shown in help/usage.
- **`description` / `usage` / `epilog`** → Human-facing help text.
- **Formatter** → Controls how help is displayed (e.g., show defaults).
- **Argument groups** → Organize flags into logical sections (e.g., “Global options”).
- **`allow_abbrev=False`** → Prevents guessy abbreviations (`--ver` → `--version`).
- **`exit_on_error=True`** → Stops execution cleanly on parse errors with a non-zero exit code.

---

## ⚙️ Built-in Actions You Get for Free

- `action="help"` → Prints help to **stdout**, exits `0`.
- `action="version"` → Prints version to **stdout**, exits `0`.

✅ Use these built-ins — they handle formatting, printing, and exit semantics correctly without custom logic.

---

## 📤 Output Channels & Exit Codes

- **`stdout`** → Normal output: help, version, regular command output.
- **`stderr`** → Problems: parse errors, invalid usage.
- **Exit codes:**  
  - `0` → success (`--help`, `--version`, or normal completion)  
  - `2` → usage or parse error (reserved by `argparse`)  

**Design choice:** “No args” prints help to **stdout** and exits `0` — a guidance flow, not an error.

---

## 🌿 Subcommands — Conceptual View

- **What they are** → Branches under the main command (e.g., `ugit init`, `ugit log`).
- **Why they matter** → Scale a single CLI into a structured command tree.
- **How they work**  
  - Declared declaratively on the parser (subparsers).
  - The chosen command is stored in the parsed namespace (`ns.cmd`).
  - Execution is delegated via a dispatcher.

- **Help UX** → Top-level help lists all subcommands; each subcommand gets its own help page.

---

## 🏗️ Separation of Concerns (Architecture)

- **Parser construction** → Defines *what* is accepted (flags, groups, subcommands, help text).
- **Behavior** → Parses input, converts `SystemExit` into an **int**, dispatches to handlers, returns **int**.
- **Execution** → The only place that calls `sys.exit(...)` — the user-facing entry point.

✅ Why this matters: keeps tests pure, UX consistent, and growth painless.

---

## 🚪 `SystemExit` — Understand It Once

`argparse` uses `SystemExit` to terminate the program *after* user-facing output:

- Help → prints to **stdout**, exits `0`
- Version → prints to **stdout**, exits `0`
- Parse errors → print to **stderr**, exit `2`

**Project convention:** Catch `SystemExit` in `main(argv)` and return an integer exit code — so tests can assert on return codes instead of exceptions.

---

## 📜 `argv` vs `sys.argv`

- **`argv` (explicit parameter)** → Passed into `main()`; pure, testable, side-effect-free.
- **`sys.argv` (global)** → Populated by the interpreter; used only at the boundary (`sys.exit(main(sys.argv[1:]))`).

✅ **Rule:** Accept `argv` explicitly everywhere except the `__main__` adapter.

---

## 🆘 Help Text That Actually Helps

- Write a clear **description** and **usage** line to orient users.
- Use **argument groups** to structure related flags.
- Choose a **formatter** that shows defaults.
- Keep `--help` fast, stable, and accurate — it’s part of your public API.

---

## 🧱 Error Handling Philosophy

- User mistakes are normal → respond with clear, actionable messages.
- Fail *early* (during parse) with a non-zero code.
- Emit help to **stderr** only when it’s part of an error; normal help goes to **stdout**.

---

## 🧪 Testing Implications

- Call the CLI as a function with **explicit `argv`**.
- Capture **stdout** / **stderr** and assert on the **exit code**.
- Avoid patching globals (`sys.argv`) or catching `SystemExit` in tests.

---

## ⚠️ Anti-Patterns to Avoid

- Mixing parsing, business logic, and `sys.exit` in one function.
- Relying on option abbreviations (surprising, non-portable).
- Printing to the wrong stream (e.g., help on stderr, errors on stdout).
- Treating testability as an afterthought (forces brittle global patching).

---

## 🔀 Migration Outlook

- This structure mirrors modern CLI frameworks (Typer, Click) conceptually.
- If you migrate later, keep the same **public surface** (`main(argv) -> int`) so tests and entry points remain stable.

---

## ✅ One-Screen Mental Checklist

- Parser declares the interface → groups, description, usage, epilog  
- Built-ins for `--help` / `--version` → let them print & exit  
- “No args” → help to **stdout**, exit `0`  
- Errors → **stderr**, exit `2`  
- `allow_abbrev=False` → no surprises  
- `main(argv)` returns **int**, handles `SystemExit`  
- Entry point → `sys.exit(main(sys.argv[1:]))`  
- Tests → pass `argv`, capture output, assert code

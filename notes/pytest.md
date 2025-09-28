# 🧪 pytest — Concepts I Actually Use

A concise, code-free guide to how this project tests its CLI with `pytest`.

---

## ❓ Why pytest

- 🪶 Minimal boilerplate → tests read like plain Python.  
- 🔍 Smart discovery & configuration → consistent across dev and CI.  
- 🧰 Powerful fixtures → reusable setup/teardown without classes.  
- 🌱 Rich ecosystem → markers, capture, monkeypatching, warnings control.

---

## 🧠 Core Mental Model

- **Test functions** → Independent checks of observable behavior.  
- **Fixtures** → Declarative providers of resources/utilities, injected by name.  
- **`conftest.py`** → Shared fixtures/config auto-discovered — no imports needed.  
- **Markers** → Labels to group, select, and organize tests.  
- **Captured I/O + exit codes** → Assert exactly what users see from the CLI.

---

## 🧰 Fixtures — Why They Matter

> [!info] A fixture is a named provider that returns something your test needs (object, function, environment) and cleans up automatically.

- **Reusable** → Define once, use everywhere.  
- **Isolated** → Fresh instance per test by default.  
- **Composable** → Fixtures can depend on other fixtures.  
- **Ergonomic** → Injected by parameter name, no manual wiring.

**Project focus:**  
- `run_cli` fixture → A “user simulator” that invokes the CLI with explicit `argv`, captures `stdout`/`stderr`, and returns the exit code.  
- ✅ Tests assert *behavior*, not implementation details.

---

## 🗂️ `conftest.py` — The Shared Toolbox

- Central place for fixtures and test utilities.  
- Auto-discovered by pytest — no need to import manually.  
- Keeps tests lean and focused on *asserting outcomes*, not plumbing.

---

## 🖨️ Capturing Output with `capsys`

- **`capsys`** → Captures **stdout** and **stderr** during a test.  
- Why: CLIs communicate via text streams; tests should validate exactly what users see.  
- Convention: help/version on **stdout**, errors on **stderr**.

---

## 🔄 `monkeypatch` vs `mock` — Different Tools

- **`monkeypatch`** (fixture) → Temporarily override attributes or environment (e.g., env vars, module attrs) for isolation.  
- **`mock`** (`unittest.mock`) → Create fakes/spies and assert interactions (calls, args) with dependencies (filesystem, network, subprocess).

**Project stance:**  
- For argument parsing and output → use `capsys` and explicit `argv`.  
- Use `mock` only when verifying interactions with external boundaries.

---

## 🏷️ Markers — Organize & Select

> [!note] Markers tag tests for targeted runs, grouping, and CI control.

- **`cli`** → Groups CLI-related tests.  
- **`slow`** → Marks long-running tests (opt-in).  

✅ Examples:  
- `pytest -m cli` → run only CLI tests.  
- `pytest -m "not slow"` → skip slow tests.

---

## ⚙️ `pytest.ini` — Behavior & Policy

- **Discovery** → Limit collection to `tests/` and known patterns.  
- **Addopts** → e.g. `-ra -x --strict-config --strict-markers --color=yes` for strict, readable runs.  
- **Warnings-as-errors** → `filterwarnings = error` surfaces tech debt early.  
- **`xfail_strict = true`** → Prevents silent passes from misused xfail.  
- **Min version** → Pin pytest to a modern baseline for consistent flags and behavior.

---

## 🧾 Exit Codes & Assertions — The CLI Mindset

- **Return codes** → Behavioral contract: `0` = success, non-zero = error.  
- **Help/version** → exit `0`, print to **stdout** (with trailing newline).  
- **Parse errors** → exit non-zero (commonly `2`), print to **stderr**.

**Project rule:**  
Tests assert **exit code**, **stdout**, and **stderr** precisely — no exceptions for “normal” paths.

---

## 🧪 Test Style for CLIs — Guiding Principles

- **Black-box** → Test observable behavior, not internals.  
- **Deterministic** → No global state; always pass explicit `argv`.  
- **Minimal** → Each test checks one behavior (no-args help, `--help`, `--version`).  
- **Composable** → As subcommands grow, reuse the same `run_cli([...])` pattern.

---

## 🧱 Isolation & Determinism

- Avoid mutating globals (e.g., `sys.argv`) in tests.  
- Prefer fixtures and explicit parameters.  
- Patch environment/time only when necessary — and let fixtures restore state automatically.

---

## ⚠️ Anti-Patterns to Avoid

- Catching `SystemExit` in normal tests → better to return an int from the CLI.  
- Printing help to **stderr** (not an error).  
- Depending on option abbreviations (surprising, non-portable).  
- Tangled setup logic → move it into fixtures.  
- Over-mocking → assert outcomes first; mock only when essential.

---

## ✅ One-Screen Checklist

- ✅ Use **fixtures** for setup; keep tests small and declarative.  
- ✅ `conftest.py` hosts shared fixtures (no imports needed).  
- ✅ Capture **stdout/stderr** with `capsys`; assert **exit codes**.  
- ✅ Tag tests with **markers** to run focused subsets in CI.  
- ✅ Enforce strictness via **pytest.ini** (warnings-as-errors, strict markers).  
- ✅ Prefer **explicit `argv`** over patching globals.  
- ✅ Mock only to verify **interactions**, not for basic output checks.

# ugit: DIY Git in Python 

Welcome aboard! We're going to implement Git in Python to learn more about how Git works on the inside.

This tutorial is different from most Git internals tutorials because we're not going to talk about Git only with words but also with code! We're going to write in Python as we go.

This is not a tutorial on using Git! To follow along I advise that you have working knowledge of Git. If you're a newcomer to Git, this tutorial is probably not the best place to start your Git journey. I suggest coming back here after you've used Git a bit and you're comfortable with making commits, branching, merging, pushing and pulling.

## Changes from the original tutorial (In Construction)

This project is inspired by the original _ugit_ tutorial, but with an important twist: instead of just replicating the code, we’re rebuilding ugit as if it were a **real-world Python project**, following today’s best practices.

Key differences:
- **Project metadata with `pyproject.toml`** &xrarr; Instead of the now-deprecated `setup.py`, we use `pyproject.toml` (PEP 621) to declare everything: project name, version, dependencies, authors, and CLI entry points. This makes the project compatible with modern build backends and installers.
- **Environment & packaging with `uv`** &xrarr; We rely on `uv`, a modern tool for dependency management and virtual environments. It replaces manual `venv` setup and traditional `pip install -e .` workflows with a faster, simpler, and reproducible system.
- **Source layout (`src/`)** &xrarr; The code lives inside `src/ugit_diy/`, following the **src-layout** packaging convention. This avoids accidental imports from the project root, ensures consistency between development and installed environments, and enforces clean project structure.
- **Package & library, not just a script** &xrarr; ugit isn’t just a throwaway script. It is structured as both a **library** (importable as `import ugit_diy`) and an **application** (runnable via `ugit` or `python -m ugit_diy`). This dual design reflects how production-grade Python projects are built.
- **Logging instead of print** &xrarr; Rather than scattering `print()` statements, we use Python’s built-in `logging` module. This allows configurable log levels, better debugging, and integration with larger systems.
- **Static typing with type hints** &xrarr; All code will use type annotations. This improves readability, catches bugs earlier, and integrates with type checkers like Pyright or MyPy.
- **Consistent formatting & linting with Ruff** &xrarr; Code style and quality are enforced automatically using Ruff (linter + formatter). This ensures clean diffs, standardized style, and fewer code review debates.
- **EditorConfig** &xrarr; You already have it—make sure it aligns with ruff/formatter so IDEs don’t fight CI.

To Do:
- **Pre-commit suite** &xrarr; Extend hooks: ruff (lint/format), pyright (type check), trailing whitespace, end-of-file, TOML/YAML/JSON checks, mdformat/markdownlint.
- **Conventional Commits + changelog** &xrarr; Enforce commit style (feat/fix/docs…) and auto-generate CHANGELOG and release notes (commitizen or semantic-release). Keeps history usable.
- **Commit hooks for code hygiene** &xrarr; We’ll use tools like **pre-commit** to automatically run checks (lint, type-checks, tests) before code is committed. This prevents bad code from ever landing in the repository.
- **CI/CD pipeline** &xrarr; We’ll add a basic GitHub Actions pipeline to automate tests, linting, and type-checking on every push. This guarantees that ugit remains stable and maintainable as it grows.
- **Docs that build** &xrarr; MkDocs + Material theme, examples, API reference (pdoc/mkdocstrings), HOWTOs, and a “Troubleshooting” page. Add a docs CI job and link checker.
- **Command-line UX polish** &xrarr; Use Typer or Click for subcommands, rich help, and shell completions. Add --version, --verbose/--quiet, colorized output (Rich), and exit codes.
- **Structured logging** &xrarr; Keep logging but consider structured JSON logs (for later piping into tools). Provide --log-level and file/console handlers.
- **Docker**
- 

In short, this isn’t just about learning Git internals — it’s also a **training ground for writing modern Python applications**. By the end, ugit won’t just be a learning project, but a fully structured, maintainable, and professional-quality application.

## Why learn Git internals?

For most tools that we use daily, we don't really care about their internals. We can use Firefox or Vim without understanding their inner workings.

At first you shouldn't care about Git internals either. You can use Git as a set of CLI commands that track code history. Run `git add, git commit` and `git push` all day long and you'll do fine, as long as you're a sole developer who just commits to one branch.

But once you start collaborating with multiple people on multiple branches and things like rebase or force push are getting involved, it's easy to become lost if you don't have a good mental model of Git internals.

From my experience with using Git myself and teaching others, a better way to improve your effectiveness with Git is by understanding how it works behind the scenes and not by learning more "advanced" Git commands. This understanding is what will allow you to solve the kind of problems that multi-user collaborative coding sometimes produce.

## Introducing: μgit

μgit (ugit) is a small implementation of a Git-like version control system (VCS). It's top goal is simplicity and educational value. ugit is implemented in small incremental steps, with each step explained in detail. Hopefully you will be able to read the small steps (explanation and code) and slowly build a complete picture of the internals.

ugit is not exactly Git, but it shares the important ideas of Git. ugit is way shorter and doesn't implement irrelevant features. For example, to reduce the complexity of ugit, ugit doesn't compress objects, doesn't save the mode of the files or doesn't save the time of a commit. But the important ideas, like commits, branches, the index, merges and remotes are all present and are very similar to Git. If you know ugit well you will be able to recognize the same ideas in Git.

This tutorial organized as a series of code changes, each change contains an explanation and the diff of the change. For example, you're now reading the first change, and you can see the code that we've added in this change as a diff on the other side. The code is an empty Python application that prints `"hello world"`.

>[!NOTE]  
> Older tutorial used `setup.py` to describe the ugit executable but that approach is deprecated. Modern Python projects use `pyproject.toml` instead as defined by PEP621. This file declares all project metadata (like name, version, authors, and dependencies) and also defines CLI entry points. In ugit, the `[project.scripts]` section in `pyproject.toml` maps the command ugit to a function inside the code, which makes it runnable directly from the shell.
> 
> To work on the project locally, we use uv, a modern package and environment manager. Instead of `python setup.py develop`, you install the project in editable mode with `uv pip install --editable .`
> - Editable mode means your source code is linked into the environment, so any changes you make to the code are immediately reflected when you run the program.
> 
> Once installed, you can run ugit either as a CLI tool (`ugit`) or as a module (`python -m ugit_diy`). Both paths are supported thanks to the combination of `pyproject.toml`, a `__main__.py` file in the package, and the CLI entry point declaration.
> 
> This modern setup ensures that ugit is both importable as a library and executable as a command-line tool, following best practices for today’s Python projects.


## Why learn Git using code?

As I mentioned earlier, in this tutorial we will actually implement Git in Python. I believe that for programmers, seeing the concepts implemented in code crystallizes understanding. It's cool to see Git explained in a diagram, but when you see the same concepts in live code that you can fully understand and actually run, a deeper understanding can be achieved. That's because if the code works no details can be omitted from it, unlike an explanation with words.


## Why not learn Git by reading the real Git code?

The real Git code is too complicated to be useful for learning basic concepts with ease. It is production quality code that is optimized for speed. It is written in C. It implements so many advanced Git features. It deals with a lot of edge cases that we don't care about for learning. In this tutorial we will focus on the bare minimum to get the point across.


## References 

>[!TIP]  
>Hi, I'm Nikita and this is a tutorial I've been working on for a long time. If you have any questions or suggestions, please leave a comment on any of the relevant sections.
>- Project Interactive Webpage : https://www.leshenko.net/p/ugit/#
>- Original Github repo of the project : https://github.com/rafifos/ugit

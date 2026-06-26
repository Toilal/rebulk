# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rebulk is a Python library for performing advanced string matching using composable patterns (string, regex, functional) and a rule engine. It is published on PyPI as `rebulk`.

## Common Commands

This project is managed with [uv](https://docs.astral.sh/uv/). Tooling lives in the
`dev` dependency group; `regex` is the optional `native` extra. Dependencies are pinned in `uv.lock`.

```bash
# Sync the dev environment (creates .venv from uv.lock, with the regex backend)
uv sync --extra native

# Run all tests (also runs module doctests + README.md doctests, see pyproject.toml addopts)
uv run pytest

# Run a single test file
uv run pytest rebulk/test/test_rebulk.py

# Run a single test
uv run pytest rebulk/test/test_rebulk.py::test_function_name -v

# Lint + format check (ruff)
uv run ruff check rebulk
uv run ruff format rebulk

# Type check (mypy)
uv run mypy

# Build sdist + wheel (uv build backend)
uv build

# Multi-version testing (tox via tox-uv: uv provisions each interpreter from the lock)
uv run tox

# Pre-commit hooks (local hooks running the dev-group tools via `uv run`)
uv run pre-commit run --all-files

# Run the suite against the `regex` backend (see remodule.py)
REBULK_REGEX_ENABLED=1 uv run pytest
```

CI runs the full matrix twice — with `REBULK_REGEX_ENABLED` set to `0` and `1` — so changes touching pattern matching must pass under both the stdlib `re` and the `regex` backend.

## Architecture

The library is built around a pipeline: **Patterns -> Matches -> Rules**.

- **`rebulk.py` / `Rebulk`** - Main entry point. Inherits from `Builder`, holds patterns, rules, and child Rebulk objects. `matches(string, context)` runs the full pipeline: pattern matching then rule execution.

- **`builder.py` / `Builder`** - Fluent API mixin providing `.string()`, `.regex()`, `.functional()`, and `.chain()` methods that create Pattern objects with configurable defaults/overrides.

- **`pattern.py`** - `Pattern` abstract base with three implementations:
  - `StringPattern` - uses `str.find`
  - `RePattern` - uses `re.finditer`
  - `FunctionalPattern` - user-provided callable
  Each pattern produces `Match` objects and applies validators, formatters, and pre/post match processors.

- **`chain.py` / `Chain`** - Ordered composition of patterns with repeaters (like regex quantifiers `?`, `*`, `+`, `{n,m}`). Also inherits from both `Pattern` and `Builder`.

- **`match.py`** - `Match` (a single match with start/end/value/name/children) and `Matches` (a list with indexed lookups by name, tag, start, end position). `MatchesDict` converts matches to an OrderedDict.

- **`rules.py`** - Rule engine. `Rule` has `when(matches, context)` / `then(matches, when_response, context)`. Built-in consequences: `RemoveMatch`, `AppendMatch`, `RenameMatch`, `AppendTags`, `RemoveTags`. Rules are topologically sorted by `priority` and `dependency`.

- **`processors.py`** - Default rules: `ConflictSolver` (keeps longer match on overlap) and `PrivateRemover` (strips private matches from final output). Priority constants `PRE_PROCESS` / `POST_PROCESS`.

- **`remodule.py`** - Conditional import: uses `regex` module instead of `re` when `REBULK_REGEX_ENABLED=1` env var is set. Enables repeated captures support.

- **`validators.py`** - Reusable validator functions (e.g., surrounding character checks). Designed to be used with `functools.partial`.

- **`introspector.py`** - Introspection utilities to extract pattern/rule metadata from a configured Rebulk.

## Key Design Points

- Fluent API: all builder methods return `self` for chaining.
- `context` dict flows through the entire pipeline (patterns, rules) enabling conditional behavior.
- Patterns can be disabled via a `disabled(context)` callable.
- Rebulk objects can be nested via `.rebulk()` to compose pattern sets.
- `marker` matches live in a separate `Matches.markers` sequence, available to rules but excluded from final results.
- The `regex` PyPI package is an optional dependency (the `native` extra in `pyproject.toml`), enabled at runtime via env var.

## Conventions

- **Conventional Commits are enforced.** CI runs `commitlint` on every push/PR, and releases are cut automatically by `python-semantic-release` from commit types (`feat:`, `fix:`, `chore:`, etc.). Non-conforming commit messages fail the pipeline. The version is the single source `pyproject.toml:project.version` (kept mirrored in `rebulk/__version__.py`) and is bumped by the release tooling — do not edit it by hand.
- Doctests run as part of the default `pytest` invocation: module docstrings (`--doctest-modules`) and the `README.md` examples (`--doctest-glob`). Keep examples version-stable across the supported Python range (e.g. avoid relying on `OrderedDict` repr, which changed in 3.12).
- Linting/formatting is **ruff** with an extended rule set (`E,W,F,I,UP,B,C4,SIM,PIE,RET,ISC,TC,FA,PT,RUF`). A `.pre-commit-config.yaml` runs ruff + mypy + commitizen as `local`/`system` hooks via `uv run`, so they use the exact versions pinned in the `dev` group / `uv.lock`.
- **The entire codebase (library + tests) is fully typed and `mypy` runs in strict mode** (`uv run mypy`). The package ships a `py.typed` marker (PEP 561), so keep new code annotated and strict-clean.

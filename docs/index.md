# Rebulk

[![Latest Version](https://img.shields.io/pypi/v/rebulk.svg)](https://pypi.python.org/pypi/rebulk)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Toilal/rebulk/blob/develop/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Toilal/rebulk/ci.yml?branch=develop)](https://github.com/Toilal/rebulk/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/Toilal/rebulk)](https://codecov.io/gh/Toilal/rebulk)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/relekang/python-semantic-release)

Rebulk is a Python library that performs advanced searches in strings that would be
hard to implement using the [`re` module](https://docs.python.org/3/library/re.html)
or [string methods](https://docs.python.org/3/library/stdtypes.html#str) alone.

It provides building blocks such as `Patterns`, `Match` and `Rule` that let you build
a custom and complex string matcher through a readable, extendable, fluent API.

The project is hosted on GitHub: <https://github.com/Toilal/rebulk>.

## Features

- **Composable patterns** — declare `string`, `regex` and `functional` patterns in bulk
  on a single `Rebulk` object using a fluent, chainable API.
- **Rich match model** — every result is a `Match` object with `value`, `start`, `end`,
  `span`, `name`, `tags` and nested `children`; the `Matches` collection offers indexed
  lookups by name, tag, position and proximity.
- **Rule engine** — express conditional post-processing (filtering, renaming, tagging,
  appending) as `Rule` classes with priorities and dependencies.
- **Chains and repeaters** — compose ordered sequences of patterns with regex-like
  quantifiers (`?`, `*`, `+`, `{n,m}`).
- **Typed retrieval** — bind a match name to its value type with `Key` for type-safe
  access, and project matches onto a dataclass or `TypedDict` with `Matches.to(...)`.
- **Optional `regex` backend** — enable the [`regex`](https://pypi.python.org/pypi/regex)
  module (repeated captures) at runtime with `REBULK_REGEX_ENABLED=1`.
- **Fully typed** — the package ships a `py.typed` marker and passes `mypy --strict`.

## Installation

```sh
pip install rebulk
```

To enable the optional [`regex`](https://pypi.python.org/pypi/regex) backend, install the
`native` extra and set the environment variable at runtime:

```sh
pip install "rebulk[native]"
export REBULK_REGEX_ENABLED=1
```

Rebulk requires Python 3.10 or later and has no runtime dependencies (the `regex`
backend is optional).

## Quickstart

Regular expression, string and function based patterns are declared on a `Rebulk`
object. It uses a fluent API to chain `string`, `regex` and `functional` methods to
define the pattern types.

```python
>>> from rebulk import Rebulk
>>> bulk = Rebulk().string('brown').regex(r'qu\w+').functional(lambda s: (20, 25))

```

Once the `Rebulk` object is fully configured, call `matches` with an input string to
retrieve all `Match` objects found by the registered patterns.

```python
>>> bulk.matches("The quick brown fox jumps over the lazy dog")
[<brown:(10, 15)>, <quick:(4, 9)>, <jumps:(20, 25)>]

```

If several `Match` objects are found at the same position, only the longer one is kept
(this is the job of the default `ConflictSolver` rule).

```python
>>> bulk = Rebulk().string('lakers').string('la')
>>> bulk.matches("the lakers are from la")
[<lakers:(4, 10)>, <la:(20, 22)>]

```

## Where to go next

- [Usage](usage.md) — build a `Rebulk`, declare the three pattern types, configure
  pattern options, and read back `Match` / `Matches`.
- [Rules & processors](rules.md) — write `Rule` classes and use the built-in
  consequences and default processors.
- [API reference](api.md) — the public symbols exported from the `rebulk` package.

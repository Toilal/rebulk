# API reference

This page lists the public symbols exported from the `rebulk` package (its `__all__`).

```python
from rebulk import (
    Rebulk, Key, Rule, CustomRule,
    AppendMatch, RemoveMatch, RenameMatch, AppendTags, RemoveTags,
    ConflictSolver, PrivateRemover,
    PRE_PROCESS, POST_PROCESS, REGEX_ENABLED,
)
```

## Rebulk

`class Rebulk(...)`

Main entry point. A `Builder` that holds patterns, rules and nested Rebulk objects, and
runs the matching pipeline. Key methods:

- `string(*patterns, key=None, **options)` — add one or more string patterns.
- `regex(*patterns, key=None, **options)` — add one or more regex patterns.
- `functional(*patterns, key=None, **options)` — add one or more functional patterns.
- `chain(**options) -> ChainBuilder` — start a chain of patterns (closed with `close()`).
- `pattern(*patterns)` — add already-built `Pattern` objects.
- `rules(*rules)` — register rules from a class, instance or module.
- `rebulk(*rebulks)` — nest other `Rebulk` objects to compose their patterns and rules.
- `defaults(**kwargs)` / `string_defaults` / `regex_defaults` / `functional_defaults` /
  `chain_defaults` — set default options for subsequently built patterns.
- `declare_keys(*keys)` — declare typed `Key` objects whose converters are inherited by
  later patterns as per-name formatters.
- `matches(string, context=None) -> Matches` — run the pipeline and return the results.
- `check_keys(*, allowed_unused=()) -> list[str]` — declared key names no pattern can
  produce (guards against typos / stale names).
- `effective_patterns(context=None)`, `effective_rules(context=None)`,
  `effective_keys(context=None)` — the patterns / rules / keys active for a given context.

## Key

`class Key(name, value_type, formatter=None)`

A frozen, generic dataclass binding a match `name` to its `value_type` for type-safe
retrieval. `formatter`, if given, is the `(str) -> T` converter applied to the matched
substring; it defaults to `value_type` itself. Passing a key to a builder method (`key=`)
wires up both the match name and the formatter, so `matches[key]` and `matches.all(key)`
return precise types instead of `Any`. `value_type` must be scalar — a dataclass or
`TypedDict` is rejected (assemble those with `Matches.to(...)`). The `converter` property
returns the effective `(str) -> T` converter.

## Rule / CustomRule

`class Rule` — abstract base for a rule. Implement `when(matches, context)` (return truthy
to trigger) and either `then(matches, when_response, context)` or a `consequence` class
attribute. Class attributes `priority` (int, higher first) and `dependency` (another rule
class) control ordering. `CustomRule` is the generic, typed rule base re-exported for
building custom rules.

## Consequences

Consequence classes applied when a rule triggers (used as a rule's `consequence`):

- `RemoveMatch` — remove the matched objects from the result.
- `AppendMatch` — append new matches to the result.
- `RenameMatch` — rename the matched objects.
- `AppendTags` — add tags to the matched objects.
- `RemoveTags` — remove tags from the matched objects.

## Default processors

- `ConflictSolver` — default `Rule` (priority `PRE_PROCESS`) that keeps the longer match
  when matches overlap.
- `PrivateRemover` — default `Rule` (priority `POST_PROCESS`) that removes matches flagged
  as `private` from the final output.

## Constants

- `PRE_PROCESS` (`2048`) — priority for rules running before the standard rules.
- `POST_PROCESS` (`-2048`) — priority for rules running after the standard rules.
- `REGEX_ENABLED` — `True` when the optional [`regex`](https://pypi.python.org/pypi/regex)
  backend is active (`REBULK_REGEX_ENABLED=1` and `regex` importable), otherwise `False`.

## Other useful modules

These are not in `__all__` but are part of the public surface:

- `rebulk.match` — the `Match` and `Matches` classes and the `MatchesDict` mapping.
- `rebulk.validators` — reusable validator functions (typically wired with
  `functools.partial`), e.g. surrounding-character checks.
- `rebulk.debug` — debug switches such as `CHECK_DECLARED_KEYS` (declared-key value-type
  contract check, off by default).
- `rebulk.introspector` — utilities to extract pattern / rule metadata from a configured
  `Rebulk`.

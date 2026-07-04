# Usage

This page covers building a `Rebulk`, declaring the three pattern types, tuning pattern
options, and reading back the `Match` / `Matches` results.

## Building a Rebulk

A `Rebulk` object collects patterns (and rules) through a fluent API: every builder
method returns the same object, so calls can be chained. Call `matches(string)` to run
the full pipeline (pattern matching, then rules) and get back a `Matches` sequence.

```python
>>> from rebulk import Rebulk
>>> bulk = Rebulk().string('brown').regex(r'qu\w+').functional(lambda s: (20, 25))
>>> bulk.matches("The quick brown fox jumps over the lazy dog")
[<brown:(10, 15)>, <quick:(4, 9)>, <jumps:(20, 25)>]

```

Rebulk objects can be nested with `Rebulk.rebulk(...)` to compose several pattern sets
into one matcher.

## String patterns

String patterns are based on
[`str.find`](https://docs.python.org/3/library/stdtypes.html#str.find), but return every
occurrence in the string. `ignore_case` can be enabled to match regardless of case.

```python
>>> Rebulk().string('la').matches("lalalilala")
[<la:(0, 2)>, <la:(2, 4)>, <la:(6, 8)>, <la:(8, 10)>]

>>> Rebulk().string('la').matches("LalAlilAla")
[<la:(8, 10)>]

>>> Rebulk().string('la', ignore_case=True).matches("LalAlilAla")
[<La:(0, 2)>, <lA:(2, 4)>, <lA:(6, 8)>, <la:(8, 10)>]

```

Several patterns can be declared with a single `string` call.

```python
>>> Rebulk().string('Winter', 'coming').matches("Winter is coming...")
[<Winter:(0, 6)>, <coming:(10, 16)>]

```

## Regular expression patterns

Regular expression patterns are based on a compiled regular expression;
[`re.finditer`](https://docs.python.org/3/library/re.html#re.finditer) is used to find
matches. All keyword arguments accepted by
[`re.compile`](https://docs.python.org/3/library/re.html#re.compile) are supported.

```python
>>> Rebulk().regex(r'l\w').matches("lolita")
[<lo:(0, 2)>, <li:(2, 4)>]

>>> import re  # import required for the flags constant
>>> Rebulk().regex('L[A-Z]KERS', flags=re.IGNORECASE) \
...         .matches("The LaKeRs are from La")
[<LaKeRs:(4, 10)>]

```

Each pattern of a single `regex` call can also be passed as a `(pattern, flags)` tuple:

```python
>>> Rebulk().regex(('L[A-Z]', re.IGNORECASE), ('L[a-z]KeRs')) \
...         .matches("The LaKeRs are from La")
[<La:(20, 22)>, <LaKeRs:(4, 10)>]

```

### The regex backend and repeated captures

If the [`regex` module](https://pypi.python.org/pypi/regex) is available and enabled
(`REBULK_REGEX_ENABLED=1`), rebulk uses it instead of the standard library `re` module,
and repeated captures are supported (`repeated_captures` defaults to `True`). Without it,
force `repeated_captures=False` to keep behaviour stable.

```python
>>> matches = Rebulk().regex(r'(\d+)(?:-(\d+))+', repeated_captures=False) \
...                   .matches("01-02-03-04")
>>> matches[0].children
[<01:(0, 2)+initiator=01-02-03-04>, <04:(9, 11)+initiator=01-02-03-04>]

```

### Abbreviations

The `abbreviations` option is a list of 2-tuples; each tuple `(old, new)` replaces
`old` with `new` in the expression before compilation — handy for reusing a separator
class across patterns.

## Functional patterns

Functional patterns are based on the evaluation of a function. The function receives the
same parameters as `Rebulk.matches` (the input string) and must return at least the
`start` and `end` indices of a `Match`. It may also return a dict of keyword arguments
for the `Match`, and may yield multiple matches.

```python
>>> def func(string):
...     index = string.find('?')
...     if index > -1:
...         return 0, index - 11
>>> Rebulk().functional(func).matches("Why do simple ? Forget about it ...")
[<Why:(0, 3)>]

```

## Chain patterns

Chain patterns are ordered compositions of string, functional and regex patterns. A
`repeater` sets repetition on each chain part, similar to regex quantifiers (`1`, `?`,
`*`, `+`, `{n,m}`). Build a chain with `chain()`, add parts, then `close()` it.

```python
>>> r = Rebulk().regex_defaults(flags=re.IGNORECASE)\
...             .defaults(children=True, formatter={'episode': int, 'version': int})\
...             .chain()\
...             .regex(r'e(?P<episode>\d{1,4})').repeater(1)\
...             .regex(r'v(?P<version>\d+)').repeater('?')\
...             .regex(r'[ex-](?P<episode>\d{1,4})').repeater('*')\
...             .close()
>>> dict(r.matches("This is E14v2-15-16-17").to_dict())
{'episode': [14, 15, 16, 17], 'version': 2}

```

## Pattern options

All patterns accept the following keyword options.

`validator`
: Function to validate the `Match` value produced by the pattern. Can be a `dict` to
  apply a validator to the match named with the key. Reusable validators live in
  `rebulk.validators` (usually wired via `functools.partial`).

`formatter`
: Function to convert the `Match` value. Can be a `dict` to format matches per name.

`pre_match_processor` / `post_match_processor`
: Function taking a single `Match`. Return `False` to invalidate the match, or a `Match`
  instance to replace the original one.

`post_processor`
: Function `(matches, pattern)` to change the default output of the pattern.

`name`
: The name of the pattern, propagated to the `Match` objects it produces.

`tags`
: A list of strings qualifying the pattern.

`value`
: Override the `value` property of the produced matches. Can be a `dict` keyed by name.

`validate_all` / `format_all`
: By default the validator/formatter apply to returned matches only; enable these to
  cover parents and children too.

`disabled`
: A `function(context)` that disables the pattern when it returns `True`.

`children`
: If `True`, return the children `Match` objects instead of a single parent match.

`private`
: If `True`, the produced matches are internal only and removed at the end of `matches`.

`private_parent` / `private_children`
: Force parent/children matches to be returned but flagged as private.

`private_names` / `ignore_names`
: Match names to flag as private / to drop from the output after validation.

`marker`
: If `True`, the produced matches are markers: excluded from the `Matches` sequence but
  available through `Matches.markers` (see [Rules & processors](rules.md)).

### Validator example

```python
>>> def check_leap_year(match):
...     return int(match.value) in [1980, 1984, 1988]
>>> Rebulk().regex(r'\d{4}', validator=check_leap_year).matches("In year 1982 ...")
[]
>>> Rebulk().regex(r'\d{4}', validator=check_leap_year).matches("In year 1984 ...")
[<1984:(8, 12)>]

```

### Defaults

`defaults(**kwargs)` sets options applied to every subsequent pattern, while
`string_defaults`, `regex_defaults`, `functional_defaults` and `chain_defaults` scope the
defaults to a single pattern type.

## Match

A `Match` is the result produced by a pattern. It exposes a `value`, position indices
(`start`, `end`, `span`), an optional `name`, `tags`, and — for structured patterns —
`children` matches (each referencing its `parent`).

When a regular expression defines groups, each group becomes a child `Match`; a named
group (`(?P<name>...)`) sets the child's `name`. The whole match (`group(0)`) becomes the
parent.

```python
>>> matches = Rebulk() \
...         .regex(r"One, (?P<one>\w+), Two, (?P<two>\w+), Three, (?P<three>\w+)") \
...         .matches("Zero, 0, One, 1, Two, 2, Three, 3, Four, 4")
>>> matches
[<One, 1, Two, 2, Three, 3:(9, 33)>]
>>> for child in matches[0].children:
...     '%s = %s' % (child.name, child.value)
'one = 1'
'two = 2'
'three = 3'

```

Use `children=True` to retrieve the children directly, and `private_parent` /
`private_children` to customise the returned structure.

## Matches

`Matches` holds the result of `matches` and behaves like a list of `Match` objects. Every
lookup method accepts an optional `predicate` callable to filter and an `index` int to
return a single element. The main methods are:

`starting(index, ...)` / `ending(index, ...)`
: Matches that start / end at a given index.

`previous(match, ...)` / `next(match, ...)`
: Matches nearest before / after a match.

`named(*names, ...)`
: Matches having any of the given names (in the order of the names).

`tagged(tag, ...)`
: Matches carrying the given tag.

`range(start=0, end=None, ...)`
: Matches within a range, sorted from start to end.

`holes(start=0, end=None, ...)`
: A *hole* match for each range where nothing matched.

`conflicting(match, ...)`
: Matches conflicting with the given match.

`at_match(match, ...)` / `at_span(span, ...)` / `at_index(pos, ...)`
: Matches at the same position / span / index.

`chain_before(position, seps, ...)` / `chain_after(position, seps, ...)`
: Chained matches before / after a position, separated only by characters from `seps`.

`names` / `tags`
: All match names / tags present in the sequence.

`markers`
: A specialised `Matches` sequence holding only marker matches.

```python
>>> matches = Rebulk().regex(r'\d{4}', name="year").string("Big Buck Bunny", name="title") \
...                   .matches("Big Buck Bunny 2008")
>>> [m.name for m in matches.named("title", "year")]
['title', 'year']

```

### Converting to a dict

`to_dict(details=False, first_value=False, enforce_list=False)` returns an ordered dict
keyed by `Match.name`. With `first_value=True`, distinct values for the same name are
wrapped into a list; with `enforce_list=True`, every value is wrapped into a list for a
predictable, typed shape; with `details=True`, values are the full `Match` objects.

## Typed retrieval

By default `Match.value` is dynamically typed (`Any`). For type-safe access, declare a
`Key` binding a match name to its value type and pass it to a builder method with `key=`.
The value type is used as the formatter, and reading back through `Matches` is fully
typed: `matches[key]` returns `T | None` and `matches.all(key)` returns `list[T]`.

```python
>>> from rebulk import Rebulk, Key
>>> year = Key("year", int)
>>> title = Key("title", str)
>>> matches = Rebulk().regex(r'\d{4}', key=year).string('Big Buck Bunny', key=title) \
...                   .matches("Big Buck Bunny 2008")
>>> matches[year]
2008
>>> matches.all(year)
[2008]
>>> matches[title]
'Big Buck Bunny'

```

For values not constructible straight from a string, pass an explicit `formatter`
(a `(str) -> T` converter):

```python
>>> from datetime import date
>>> released = Key("released", date, formatter=date.fromisoformat)
>>> Rebulk().regex(r'\d{4}-\d{2}-\d{2}', key=released).matches("on 2008-01-02")[released]
datetime.date(2008, 1, 2)

```

A `children=True` pattern with several named groups accepts a sequence of keys on the same
`key=` parameter; each key's converter is registered as a per-name formatter.

```python
>>> season = Key("season", int)
>>> episode = Key("episode", int)
>>> matches = Rebulk().regex(r'S(?P<season>\d+)E(?P<episode>\d+)',
...                          key=[season, episode], children=True) \
...                   .matches("Show.S03E07.mkv")
>>> matches[season], matches[episode]
(3, 7)

```

### Declaring keys once

To avoid repeating per-name formatters across many patterns, declare the keys once on the
builder with `declare_keys`. Every pattern built afterwards inherits each key's converter
for the matching group name (a pattern-level `formatter` still overrides it).

```python
>>> rb = Rebulk().declare_keys(season, episode)
>>> _ = rb.regex(r'S(?P<season>\d+)E(?P<episode>\d+)', children=True)
>>> _ = rb.regex(r'(?P<season>\d+)x(?P<episode>\d+)', children=True)
>>> matches = rb.matches("Show.S03E07.mkv")
>>> matches[season], matches[episode]
(3, 7)

```

### Projecting onto a dataclass or TypedDict

`Matches.to(...)` projects matches onto a typed target. Each field is filled from matches
sharing its name: a `list[...]` field collects all values, any other field takes the
first, and unmatched fields fall back to their default.

```python
>>> from dataclasses import dataclass, field
>>> @dataclass
... class Movie:
...     year: int
...     title: str
...     tags: list[str] = field(default_factory=list)
>>> tag = Key("tags", str)
>>> matches = Rebulk().regex(r'\d{4}', key=year).string('Big Buck Bunny', key=title) \
...                   .string('HD', key=tag).string('BluRay', key=tag) \
...                   .matches("Big Buck Bunny 2008 HD BluRay")
>>> matches.to(Movie)
Movie(year=2008, title='Big Buck Bunny', tags=['HD', 'BluRay'])

```

`to` also accepts a `TypedDict` (unmatched keys are omitted), a primitive type (returns
the first value), or a `list[...]` of a scalar type (returns all values). A `list` of a
dataclass or `TypedDict` is rejected, as a flat match sequence has no record grouping.

### Verifying declared keys

Keys declared with `declare_keys` are carried on the resulting `Matches` (as
`matches.declared_keys`) and let `to` close the typing loop: a model field whose type
contradicts a declared key of the same name raises `TypeError`.

Because a declared key binds by *name*, a typo or a stale name silently no-ops.
`check_keys()` returns the declared key names that no built pattern can produce; assert its
result in a test so a typo fails fast. Names produced only by a rule or dynamically by a
functional pattern can be passed to `allowed_unused`, or declared through a functional
pattern's `properties` mapping.

```python
>>> rb = Rebulk().declare_keys(Key('season', int), Key('seson', int)) \
...        .regex(r'S(?P<season>\d+)', children=True)
>>> rb.check_keys()
['seson']
>>> rb.check_keys(allowed_unused=['seson'])
[]

```

An opt-in contract check (`rebulk.debug.CHECK_DECLARED_KEYS = True`, or env
`REBULK_CHECK_DECLARED_KEYS=1`) additionally asserts at match time that every named value
is an instance of its declared key's `value_type`. It is off by default (zero production
cost) — enable it in development or CI to catch a formatter override producing the wrong
type.

# Rules & processors

Rules are a convenient, readable way to implement advanced conditional logic across
several `Match` objects. When a rule is triggered it performs an action on the `Matches`
object — filtering out matches, adding tags, renaming, appending, and so on.

## Markers

Patterns declared with `marker=True` produce marker matches. They are excluded from the
`Matches` sequence but available through `Matches.markers`, a specialised `Matches`
sequence supporting all the same lookup methods.

Marker matches are not intended for the final result, but they are useful when
implementing a `Rule` — for instance to mark regions (groups, paths) that a rule then
reasons about.

## Writing a rule

Rules extend the abstract `Rule` class and are registered with `Rebulk.rules(...)`, which
accepts a `Rule` instance, a `Rule` class, or a module containing only `Rule` classes.

A rule triggers when its `when(matches, context)` method returns a truthy value — `True`,
a non-empty list of `Match` objects, or any other truthy object. When triggered, its
`then(matches, when_response, context)` method performs the action, receiving the value
returned by `when` as `when_response`.

```python
>>> from rebulk import Rebulk, Rule, RemoveMatch

>>> class FirstOnlyRule(Rule):
...     consequence = RemoveMatch
...
...     def when(self, matches, context):
...         grabbed = matches.named("grabbed", 0)
...         if grabbed and matches.previous(grabbed):
...             return grabbed

>>> rebulk = Rebulk()
>>> _ = rebulk.regex("This match(.*?)grabbed", name="grabbed")
>>> _ = rebulk.regex("if it's(.*?)first match", private=True)
>>> _ = rebulk.rules(FirstOnlyRule)

>>> rebulk.matches("This match is grabbed only if it's the first match")
[<This match is grabbed:(0, 21)+name=grabbed>]
>>> rebulk.matches("if it's NOT the first match, This match is NOT grabbed")
[]

```

## Consequences

Instead of implementing `then` yourself, declare a `consequence` class attribute with a
`Consequence` class or instance. The built-in consequences are:

- `RemoveMatch` — remove the matched objects from the result.
- `AppendMatch` — add new matches to the result.
- `RenameMatch(name)` — rename matched objects.
- `AppendTags(tags)` — add tags to matched objects.
- `RemoveTags(tags)` — remove tags from matched objects.

A list of consequences is also supported: `when_response` must then be iterable, and each
element is handed to the corresponding consequence in the same order.

## Priority and dependencies

When several rules are registered, set the `priority` class attribute (an integer — higher
runs first) to order their execution, and declare a `dependency` on another `Rule` class
to force it to run before the current one. For all rules sharing the same `priority`,
every `when` is evaluated before any `then` is called. Rules are topologically sorted from
these constraints.

## Default processors

Two default rules ship in `rebulk.processors` and run on every `Rebulk.matches` call:

- **`ConflictSolver`** (priority `PRE_PROCESS`) — when matches overlap, it keeps the
  longer one. A pattern can customise this per match with a `conflict_solver` callable
  `(match, conflicting_match)`; returning the conflicting match removes it, and returning
  the `"__default__"` string falls back to the longer-match behaviour.
- **`PrivateRemover`** (priority `POST_PROCESS`) — strips matches flagged as `private`
  from the final output.

The priority constants `PRE_PROCESS` (`2048`) and `POST_PROCESS` (`-2048`) are exported
from the `rebulk` package so custom rules can position themselves relative to these
defaults.

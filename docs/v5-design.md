# Rebulk v5 — design analysis

Tracking issue: [#43](https://github.com/Toilal/rebulk/issues/43). This document is the
design reference for the v5 work. It is intentionally **ergonomics-first**: every
proposal is judged on *"is the common case still short and obvious for the developer?"*
before *"is it type-safe?"*.

## 1. Goals & principles

1. **Type-safe where it counts, invisible elsewhere.** The dynamic engine stays dynamic;
   typing is a thin, *opt-in* facade at the boundaries where developers read values.
2. **The common case stays a one-liner.** Adding types must never force boilerplate on
   code that didn't ask for it. `Rebulk().regex(...).matches(s)` keeps working untouched.
3. **Backwards-compatible by default.** Most of v5 is *additive*. The few real breaks are
   listed explicitly and each gets a mechanical migration step.
4. **No new runtime dependencies.** (Same rule that kept `toposort` vendored.)

The guiding test for every item below: *would a guessit-style consumer write less, clearer
code with this?*

## 2. Already shipped (4.2.x — the foundation)

These landed before v5 and are the base the rest builds on:

- `Key[T]` — a typed handle binding a match name to its value type:
  `matches[YEAR] -> int | None`, `matches.all(YEAR) -> list[int]`.
- `Matches.to(model)` — projects named matches onto a `dataclass` / `TypedDict`, plus a
  primitive (`to(int)`) or `list[<scalar>]`; `list[<structured>]` is rejected (no record
  grouping).
- `Matches.named(*names)` — any-of selection.
- Guard: a `dataclass`/`TypedDict` is rejected as a `Key.value_type`.

Everything below is **remaining** v5 work.

---

## 3. Work items

Each item: **Problem → Proposed API (with before/after) → Breaking? → Effort → Migration.**

### 3.1 Decouple `Chain` from `Builder` (architecture)

**Problem.** `class Chain(Pattern, Builder)` inherits from both, which:
- forces a deferred `from .chain import Chain` inside `Builder.build_chain` (circular import);
- violates Liskov — `Chain.pattern()` returns `ChainPart` instead of `Self`
  (`# type: ignore[override]`), and `ChainPart.regex/string/functional` are typed `-> Any`;
- makes `Builder` impossible to parametrise cleanly (blocks 3.2).

**Proposed API.** Split the *matchable* `Chain` (a `Pattern`) from the *fluent builder*
that assembles it. Crucially, **the fluent API the developer writes is unchanged** — the
change is internal (the only visible shift is the static return type of `.chain()`, from
`Chain` to `ChainBuilder`, which is invisible to code that doesn't annotate it):

```python
# UNCHANGED for the developer:
Rebulk() \
    .chain() \
        .regex(r'e(?P<episode>\d+)').repeater(1) \
        .regex(r'v(?P<version>\d+)').repeater('?') \
    .close()
```

Internally:
- `Chain(Pattern)` — only the matchable side (`_match`, `patterns`, repeaters state).
- `ChainBuilder` — returned by `.chain()`, holds the `Chain` being built, exposes
  `.regex/.string/.functional` (returning `ChainPart` so `.repeater()` still chains) and
  `.close()`. No `Pattern` inheritance, no circular import, no Liskov `type: ignore`,
  and `ChainPart.regex/string/functional` get real return types instead of `Any`.

**Breaking?** *Almost none.* `Chain` is not in `rebulk.__all__`; only code that imports
`rebulk.chain.Chain` and relies on it *being a `Builder`* (e.g. `isinstance(chain, Builder)`)
breaks — extremely rare. The fluent API is unchanged.

**Effort.** Medium (internal restructuring of `chain.py` + `builder.build_chain`).

**Migration.** None for the documented fluent API. Note in migration guide: "`Chain` is no
longer a `Builder` subclass; build chains through `.chain()` as documented."

---

### 3.2 Typed `context` — `Rebulk[Ctx]` (the expensive one)

**Problem.** `context: dict[str, Any]` flows through ~everything (323 sites across 7 modules:
`matches()`, `when/then`, `disabled(context)`, processors). It is the last big `Any` in the
public surface.

**Honest cost/benefit.** Full genericity (`Rebulk[Ctx]`, `Rule[Ctx]`, `Pattern[Ctx]`, …) is
**very invasive** and hurts ergonomics:
- `context` is consumed ad-hoc inside user rules; threading `Ctx` requires every `Rule` to
  become generic too.
- Rules/patterns are usually defined *separately* from the `Rebulk` instance, so the `Ctx`
  type does not flow naturally to where it's used.
- A default type parameter (`Rebulk()` ≡ `Rebulk[dict[str, Any]]`) needs PEP 696 `TypeVar`
  defaults — native only on 3.13+, otherwise via `typing_extensions`.

**Recommendation: do NOT make the whole stack generic.** Instead, offer a *lightweight,
opt-in* convention that costs nothing for those who don't want it:

```python
from typing import TypedDict

class Ctx(TypedDict, total=False):
    year_min: int
    allowed: list[str]

class MyRule(Rule):
    def when(self, matches: Matches, context: Ctx | None) -> Any:   # user annotates locally
        if context and context.get("year_min"):
            ...
```

i.e. keep the library on `dict[str, Any]` (or widen to `Mapping[str, Any]`) and let users
annotate `context` with their own `TypedDict` in their own rules. Document this pattern.

If genericity is still wanted later, gate it behind `Rebulk[Ctx]` with a PEP 696 default so
`Rebulk()` keeps meaning `Rebulk[dict[str, Any]]` — but only once 3.10/3.11 are dropped, to
avoid a `typing_extensions` runtime dep.

**Breaking?** The lightweight path: none. The generic path: potentially a min-Python bump.

**Effort.** Lightweight: trivial (docs). Generic: large.

**Migration.** Lightweight path needs none.

---

### 3.3 Formatter-based `Key`

**Problem.** `Key(name, value_type)` uses `value_type` as *both* the `T` marker and the
`(str) -> T` converter. That only works for scalars constructible from a string
(`int`, `str`, `float`). A value parsed by a custom function (a date, an enum, a model) can't
be expressed.

**Proposed API.** Add an optional `formatter`, defaulting to `value_type`:

```python
@dataclass(frozen=True)
class Key(Generic[T]):
    name: str
    value_type: type[T]
    formatter: Callable[[str], T] | None = None   # defaults to value_type

# unchanged:
YEAR = Key("year", int)
# new — custom converter, still fully typed as date:
from datetime import date
RELEASED = Key("released", date, formatter=date.fromisoformat)

matches[RELEASED]   # -> date | None
```

`_apply_key` wires `formatter=key.formatter or key.value_type`.

**Breaking?** No — additive field with a default.

**Effort.** Small.

**Migration.** None.

---

### 3.4 Nested / record models — `to(list[Model])`

**Problem.** `to(list[Movie])` is currently rejected: a `Matches` is a *flat* sequence with
no notion of a "record", so there's no canonical way to group matches into N items. (Note:
the guessit audit showed **no current demand** for this — keep it low priority.)

**Proposed API (exploratory).** Introduce an explicit grouping boundary, reusing the
existing `Match.parent` / marker concept:

```python
# group by the parent match (e.g. each "filepart" marker = one record):
matches.to(list[Episode], group="filepart")
```

Each group of matches sharing the boundary becomes one `Episode`, populated by name as in the
scalar `to()`. Without an explicit `group=`, `to(list[Model])` stays rejected (no silent
guessing).

**Breaking?** No — additive, and the rejected case stays rejected.

**Effort.** Medium-high (needs the grouping semantics nailed down). **Recommendation:**
defer until a real use case appears; ship a clear `NotImplementedError` message meanwhile.

---

### 3.5 Predictable `to_dict`

**Problem.** `to_dict()[name]` returns a *scalar or a list* depending on how many matches
share the name — untypable, forces `isinstance` checks downstream.

**Status.** Largely **superseded** by `to(model)` (declares list-vs-scalar per field) and by
`Key`/`all`. `to_dict` itself must stay for backwards compat (guessit relies on it heavily).

**Proposed API.** Don't change `to_dict`'s default. Offer a predictable, typed sibling:

```python
matches.to_dict(enforce_list=True)   # already exists -> every value is a list
# documented return shape: dict[str, list[Any]]  (predictable, typable)
```

and steer the docs toward `to(model)` / `Key` for typed access. Optionally a thin
`to_mapping() -> dict[str, list[Any]]` alias if a clearer name helps.

**Breaking?** No.

**Effort.** Small (mostly docs + typing the `enforce_list=True` shape).

---

## 4. Sequencing & versioning

Dependency order (do earlier items first to avoid rework):

1. **3.1 Chain/Builder decoupling** — unblocks any future `Builder` parametrisation, removes
   the circular import. Internal, near-zero breakage. *Do first.*
2. **3.3 Formatter `Key`** — small, additive, high value. Can ship anytime.
3. **3.5 `to_dict` predictability** — docs + typing, anytime.
4. **3.2 `context`** — adopt the *lightweight* convention (docs only). Defer true
   `Rebulk[Ctx]` genericity unless 3.10/3.11 are dropped.
5. **3.4 nested models** — defer until demand exists.

**Does this need a major bump?** Most items are additive (could ship as 4.x minors). A
**v5 major** is justified only if we also: (a) make `Chain` formally not-a-`Builder` and
accept the rare break, and/or (b) bump the minimum Python (enabling PEP 696 for `Rebulk[Ctx]`
and dropping the last dead-code paths). Recommendation: batch the (small) breaking bits into
one **v5.0.0** so users migrate once, ship the additive bits as they're ready.

---

## 5. Migration note (draft for the docs)

> To be published as `docs/migration-v5.md` / release notes when v5 ships.

### What does **not** change
- Building patterns: `Rebulk().string()/.regex()/.functional()/.chain()...` — identical.
- `matches(string, context)`, rules (`when`/`then`), `to_dict()` defaults — identical.
- `Match`, `Matches`, all query methods — identical.

### What's new (opt-in, no migration needed)
- **Typed keys:** `YEAR = Key("year", int)`, then `matches[YEAR] -> int | None`,
  `matches.all(YEAR) -> list[int]`. Custom converters: `Key("released", date, formatter=...)`.
- **Typed results:** `matches.to(MyDataclass)` / `matches.to(MyTypedDict)` /
  `matches.to(int)` / `matches.to(list[int])`.
- **Multi-name selection:** `matches.named("title", "episode_title")`.
- **Typed context (convention):** annotate `context` with your own `TypedDict` in your rules.

### Breaking changes (mechanical)
- **`Chain` is no longer a `Builder` subclass.** Build chains via the documented `.chain()`
  fluent API (unchanged). Only affects code importing `rebulk.chain.Chain` and relying on it
  being a `Builder` (e.g. `isinstance(chain, Builder)`).
- *(if min-Python is bumped)* Rebulk v5 requires Python ≥ 3.x — update your environment.

### Recommended modernisations (optional)
- Replace `matches.to_dict()` + manual `isinstance(v, list)` with `matches.to(Model)` or
  `Key`-based access for predictable, typed values.
- Replace `(*matches.named("a"), *matches.named("b"))` with `matches.named("a", "b")`.

---

## 6. Open questions

1. **Major bump or not?** Batch the small breaks into v5.0.0, or keep shipping additive 4.x
   and avoid the `Chain` break entirely (keep it a `Builder` but deprecated)?
2. **Minimum Python for v5** — keep 3.10, or drop to 3.11/3.12 to unlock PEP 696 defaults
   (and a cleaner `Rebulk[Ctx]`) without a `typing_extensions` runtime dep?
3. **`to_dict` future** — soft-deprecate in favour of `to()`, or keep as a first-class API?
4. **Nested models** — is there a real consumer? (guessit currently isn't one.)

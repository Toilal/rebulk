#!/usr/bin/env python
"""
Tests for typed Key retrieval (POC for type-safe value access).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, TypedDict

import pytest

from ..key import Key
from ..rebulk import Rebulk

if TYPE_CHECKING:
    from typing_extensions import assert_type

    from ..match import Match


def test_key_scalar_retrieval() -> None:
    year = Key("year", int)
    title = Key("title", str)

    bulk = Rebulk().regex(r"\d{4}", key=year).string("Big Buck Bunny", key=title)
    matches = bulk.matches("Big Buck Bunny 2008")

    assert matches[year] == 2008
    assert matches.all(year) == [2008]
    assert matches[title] == "Big Buck Bunny"


def test_key_converter_defaults_to_value_type() -> None:
    assert Key("year", int).converter is int
    fmt = date.fromisoformat
    assert Key("released", date, formatter=fmt).converter is fmt


def test_key_with_explicit_formatter() -> None:
    released = Key("released", date, formatter=date.fromisoformat)
    matches = Rebulk().regex(r"\d{4}-\d{2}-\d{2}", key=released).matches("on 2008-01-02 ...")

    assert matches[released] == date(2008, 1, 2)
    assert matches.all(released) == [date(2008, 1, 2)]


def test_key_rejects_structured_value_type() -> None:
    @dataclass
    class Movie:
        year: int
        title: str

    class MovieDict(TypedDict):
        year: int
        title: str

    with pytest.raises(TypeError, match=r"Matches\.to"):
        Key("movie", Movie)
    with pytest.raises(TypeError, match=r"Matches\.to"):
        Key("movie", MovieDict)


def test_key_missing_returns_none() -> None:
    year = Key("year", int)
    matches = Rebulk().regex(r"\d{4}", key=year).matches("no digits here")

    assert matches[year] is None
    assert matches.all(year) == []


def test_key_multiple_values() -> None:
    digit = Key("digit", int)
    matches = Rebulk().regex(r"\d", key=digit).matches("1 2 3")

    assert matches.all(digit) == [1, 2, 3]
    assert matches[digit] == 1


def test_keys_children_per_name_formatter() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    bulk = Rebulk().regex(r"S(?P<season>\d+)E(?P<episode>\d+)", keys=[season, episode], children=True)
    matches = bulk.matches("Show.S03E07.mkv")

    assert matches[season] == 3
    assert matches[episode] == 7


def test_keys_multiple_children_values() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    bulk = Rebulk().regex(
        r"S(?P<season>\d+)(?:E(?P<episode>\d+))+",
        keys=[season, episode],
        children=True,
    )
    matches = bulk.matches("Show.S03E07.mkv")

    assert matches[season] == 3
    assert matches.all(episode) == [7]


def test_keys_preserve_explicit_per_name_formatter() -> None:
    season = Key("season", int)
    episode = Key("episode", str)

    # An explicit per-name formatter wins over the key converter (variance preserved):
    # the key would apply plain str, the override upper-cases instead.
    bulk = Rebulk().regex(
        r"S(?P<season>\d+)E(?P<episode>\w+)",
        keys=[season, episode],
        formatter={"episode": str.upper},
        children=True,
    )
    matches = bulk.matches("Show.S03Eab.mkv")

    assert matches[season] == 3
    assert matches[episode] == "AB"


def test_keys_rejects_single_formatter_callable() -> None:
    season = Key("season", int)

    with pytest.raises(TypeError, match=r"per-name formatter"):
        Rebulk().regex(r"(?P<season>\d+)", keys=[season], formatter=int, children=True)


def test_keys_none_is_noop() -> None:
    year = Key("year", int)
    matches = Rebulk().regex(r"\d{4}", key=year, keys=None).matches("born in 1984")

    assert matches[year] == 1984


def test_declare_keys_inherited_per_name_formatter() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    bulk = Rebulk().declare_keys(season, episode)
    # No keys=/formatter= on the pattern: the converters are inherited from the registry.
    bulk.regex(r"S(?P<season>\d+)E(?P<episode>\d+)", children=True)
    matches = bulk.matches("Show.S03E07.mkv")

    assert matches[season] == 3
    assert matches[episode] == 7


def test_declare_keys_inherited_on_named_parent() -> None:
    year = Key("year", int)

    bulk = Rebulk().declare_keys(year).regex(r"\d{4}", name="year")
    matches = bulk.matches("born in 1984")

    assert matches[year] == 1984


def test_declare_keys_explicit_formatter_overrides_registry() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    bulk = Rebulk().declare_keys(season, episode)
    # roman/CJK-like pattern: a per-pattern formatter for episode wins over the registry int.
    bulk.regex(
        r"S(?P<season>\d+)E(?P<episode>\w+)",
        formatter={"episode": lambda s: len(s)},
        children=True,
    )
    matches = bulk.matches("Show.S03Eabcd.mkv")

    assert matches[season] == 3
    assert matches.all(episode) == [4]


def test_declare_keys_bare_callable_formatter_wins() -> None:
    # A single bare-callable formatter is the pattern's explicit choice and must
    # win over the registry converter (variance preserved, even without a dict).
    year = Key("year", int)
    bulk = Rebulk().declare_keys(year).regex(r"\d{4}", name="year", formatter=lambda s: f"Y{s}")
    matches = bulk.matches("born in 1984")

    assert matches[0].value == "Y1984"


def test_declare_keys_does_not_mutate_shared_default_formatter() -> None:
    season = Key("season", int)
    shared = {"x": str.upper}
    bulk = Rebulk().declare_keys(season).defaults(formatter=shared)
    bulk.regex(r"(?P<season>\d+)", children=True)

    # The caller-owned dict and the stored default must stay pristine.
    assert shared == {"x": str.upper}
    assert "season" not in bulk._defaults["formatter"]


def test_keys_does_not_mutate_caller_formatter_dict() -> None:
    season = Key("season", int)
    episode = Key("episode", int)
    shared = {"episode": str.upper}
    Rebulk().regex(r"S(?P<season>\d+)E(?P<episode>\w+)", keys=[season, episode], formatter=shared, children=True)

    # keys= must not leak the season converter into the caller's dict.
    assert shared == {"episode": str.upper}


def test_declare_keys_returns_self_for_chaining() -> None:
    year = Key("year", int)
    bulk = Rebulk()
    assert bulk.declare_keys(year) is bulk


def test_declare_keys_inherited_in_chain() -> None:
    episode = Key("episode", int)
    version = Key("version", int)

    # The ticket's motivating example: declare_keys replaces the repeated
    # formatter={"episode": int, "version": int} on the chain.
    rebulk = (
        Rebulk()
        .declare_keys(episode, version)
        .regex_defaults(flags=re.IGNORECASE)
        .defaults(children=True)
        .chain()
        .regex(r"e(?P<episode>\d{1,4})")
        .repeater(1)
        .regex(r"v(?P<version>\d+)")
        .repeater("?")
        .regex(r"[ex-](?P<episode>\d{1,4})")
        .repeater("*")
        .close()
    )
    matches = rebulk.matches("This is E14v2-15-16-17")

    assert matches.all(episode) == [14, 15, 16, 17]
    assert matches[version] == 2


def test_declared_keys_carried_on_matches() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    matches = Rebulk().declare_keys(season, episode).matches("Show.S03E07.mkv")

    assert matches.declared_keys == {"season": season, "episode": episode}


def test_declared_keys_empty_without_declaration() -> None:
    # key= wires a pattern but does not populate the declared registry.
    year = Key("year", int)
    matches = Rebulk().regex(r"\d{4}", key=year).matches("1984")

    assert matches.declared_keys == {}


def test_effective_keys_merges_children() -> None:
    season = Key("season", int)
    episode = Key("episode", int)

    child = Rebulk().declare_keys(episode)
    parent = Rebulk().declare_keys(season).rebulk(child)

    assert parent.effective_keys() == {"season": season, "episode": episode}

    # Effective keys flow onto the produced Matches too.
    matches = parent.matches("nothing")
    assert matches.declared_keys == {"season": season, "episode": episode}


def test_effective_keys_parent_wins_over_child() -> None:
    parent_key = Key("dup", int)
    child_key = Key("dup", str)

    parent = Rebulk().declare_keys(parent_key).rebulk(Rebulk().declare_keys(child_key))

    assert parent.effective_keys() == {"dup": parent_key}


if TYPE_CHECKING:

    def _reveal_types() -> None:
        # Type-checked only (never executed): the typed key drives precise types.
        year = Key("year", int)
        title = Key("title", str)
        matches = Rebulk().regex(r"\d{4}", key=year).string("x", key=title).matches("2008 x")

        assert_type(matches[year], "int | None")
        assert_type(matches.all(year), list[int])
        assert_type(matches[title], "str | None")
        # A formatter-based key keeps the precise value type.
        released = Key("released", date, formatter=date.fromisoformat)
        assert_type(matches[released], "date | None")
        # Existing integer / slice access stays intact.
        assert_type(matches[0], Match)

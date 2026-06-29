#!/usr/bin/env python
"""
Tests for typed Key retrieval (POC for type-safe value access).
"""

from __future__ import annotations

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

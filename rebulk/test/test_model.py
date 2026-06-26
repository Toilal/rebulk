#!/usr/bin/env python
"""
Tests for typed result models via Matches.to(dataclass) (v5 POC).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

import pytest

from ..key import Key
from ..rebulk import Rebulk

if TYPE_CHECKING:
    from typing_extensions import assert_type


@dataclass
class Movie:
    year: int
    title: str
    tags: list[str] = field(default_factory=list)
    resolution: str | None = None


class MovieDict(TypedDict):
    year: int
    title: str
    tags: list[str]


def test_to_model() -> None:
    year = Key("year", int)
    title = Key("title", str)
    tag = Key("tags", str)

    bulk = (
        Rebulk()
        .regex(r"\d{4}", key=year)
        .string("Big Buck Bunny", key=title)
        .string("HD", key=tag)
        .string("BluRay", key=tag)
    )
    movie = bulk.matches("Big Buck Bunny 2008 HD BluRay").to(Movie)

    assert movie == Movie(year=2008, title="Big Buck Bunny", tags=["HD", "BluRay"], resolution=None)


def test_to_model_defaults_when_unmatched() -> None:
    year = Key("year", int)
    title = Key("title", str)

    movie = Rebulk().regex(r"\d{4}", key=year).string("Title", key=title).matches("Title 1999").to(Movie)

    assert movie.tags == []  # list field -> empty
    assert movie.resolution is None  # optional scalar -> default


def test_to_typeddict() -> None:
    year = Key("year", int)
    title = Key("title", str)
    tag = Key("tags", str)

    bulk = (
        Rebulk()
        .regex(r"\d{4}", key=year)
        .string("Big Buck Bunny", key=title)
        .string("HD", key=tag)
        .string("BluRay", key=tag)
    )
    movie = bulk.matches("Big Buck Bunny 2008 HD BluRay").to(MovieDict)

    assert movie == {"year": 2008, "title": "Big Buck Bunny", "tags": ["HD", "BluRay"]}


def test_to_typeddict_omits_unmatched() -> None:
    year = Key("year", int)
    movie = Rebulk().regex(r"\d{4}", key=year).matches("1999").to(MovieDict)

    assert movie == {"year": 1999, "tags": []}  # unmatched scalar key omitted, list key kept


def test_to_requires_dataclass_or_typeddict() -> None:
    matches = Rebulk().string("x").matches("x")
    with pytest.raises(TypeError, match="not a dataclass or TypedDict"):
        matches.to(int)


if TYPE_CHECKING:

    def _reveal_types() -> None:
        movie = Rebulk().matches("").to(Movie)
        assert_type(movie, Movie)
        movie_dict = Rebulk().matches("").to(MovieDict)
        assert_type(movie_dict, MovieDict)

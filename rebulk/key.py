#!/usr/bin/env python
"""
Typed keys binding a match name to its value type for type-safe retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Key(Generic[T]):
    r"""
    A typed handle for a named match.

    ``name`` is the match name to declare and look up; ``value_type`` is the type
    of the match value and the ``(str) -> T`` converter applied to produce it
    (e.g. ``int``, ``str``, ``float``). Passing a key to a builder method
    (``key=...``) wires up both the match ``name`` and ``formatter``, so that
    ``matches[key]`` and ``matches.all(key)`` return precise types instead of
    ``Any``.

    >>> from rebulk import Rebulk, Key
    >>> year = Key("year", int)
    >>> Rebulk().regex(r"\d{4}", key=year).matches("born in 1984")[year]
    1984
    """

    name: str
    value_type: type[T]

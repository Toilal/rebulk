#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..match import Match
from rebulk.pattern import StringPattern


def test_equality():
    p = StringPattern("test")

    m1 = Match(p, 1, 3, value="es")
    m2 = Match(p, 1, 3, value="es")

    other = object()

    assert hash(m1) == hash(m2)
    assert m1 == m2

    assert m1 != other

    assert str(m1) == 'Match<span=(1, 3), value=\'es\'>'

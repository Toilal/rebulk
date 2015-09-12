#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..match import Match
from ..pattern import StringPattern


class TestMatchClass:
    p = StringPattern("test")

    def test_str(self):
        m1 = Match(self.p, 1, 3, value="es")

        assert str(m1) == 'Match<span=(1, 3), value=\'es\'>'

    def test_equality(self):
        m1 = Match(self.p, 1, 3, value="es")
        m2 = Match(self.p, 1, 3, value="es")

        assert hash(m1) == hash(m2)

        assert m1 == m2

    def test_inequality(self):
        m1 = Match(self.p, 0, 2, value="te")
        m2 = Match(self.p, 2, 4, value="st")
        m3 = Match(self.p, 0, 2, value="other")

        other = object()

        assert hash(m1) != hash(m2)
        assert hash(m1) != hash(m3)

        assert m1 != other
        assert m1 != m2
        assert m1 != m3

    def test_length(self):
        m1 = Match(self.p, 0, 4, value="test")
        m2 = Match(self.p, 0, 2, value="spanIsUsed")

        assert len(m1) == 4
        assert len(m2) == 2

    def test_compare(self):
        m1 = Match(self.p, 0, 2, value="te")
        m2 = Match(self.p, 2, 4, value="st")

        assert m1 < m2
        assert m1 <= m2

        assert m2 > m1
        assert m2 >= m1

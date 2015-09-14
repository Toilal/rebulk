#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import six

from ..match import Match, group_neighbors
from ..pattern import StringPattern


class TestMatchClass:
    p = StringPattern("test")

    def test_str(self):
        m1 = Match(self.p, 1, 3, value="es")

        assert str(m1) == 'Match<span=(1, 3), value=\'es\'>'

    def test_equality(self):
        m1 = Match(self.p, 1, 3, value="es")
        m2 = Match(self.p, 1, 3, value="es")

        other = object()

        assert hash(m1) == hash(m2)
        assert hash(m1) != hash(other)

        assert m1 == m2
        assert not m1 == other

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

        other = object()

        assert m1 < m2
        assert m1 <= m2

        assert m2 > m1
        assert m2 >= m1

        if six.PY3:
            with pytest.raises(TypeError):
                m1 < other

            with pytest.raises(TypeError):
                m1 <= other

            with pytest.raises(TypeError):
                m1 > other

            with pytest.raises(TypeError):
                m1 >= other


class TestMatchFunctions:
    def test_group_neighbors(self):
        input_string = "abc.def._._.ghi.klm.nop.qrs.tuv.wyx.z"

        matches = StringPattern("abc", "def", "ghi", "nop", "qrs.tuv", "z").matches(input_string)
        matches_groups = list(group_neighbors(matches, input_string, "._"))

        assert len(matches_groups) == 3
        assert len(matches_groups[0]) == 3
        assert len(matches_groups[1]) == 2
        assert len(matches_groups[2]) == 1

        abc, def_, ghi = matches_groups[0]
        assert abc.value == "abc"
        assert def_.value == "def"
        assert ghi.value == "ghi"

        nop, qrstuv = matches_groups[1]
        assert nop.value == "nop"
        assert qrstuv.value == "qrs.tuv"

        z = matches_groups[2][0]
        assert z.value == "z"

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import six

from ..match import Match, Matches, group_neighbors
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


class TestMatchesClass:
    p = StringPattern("test")

    m1 = Match(p, 0, 2, value="te")
    m2 = Match(p, 2, 3, value="s")
    m3 = Match(p, 3, 4, value="t")
    m4 = Match(p, 2, 4, value="st")

    def test_base(self):
        l = Matches()
        l.append(self.m1)

        assert len(l) == 1
        assert list(l.starting(0)) == [self.m1]
        assert list(l.ending(2)) == [self.m1]

        l.append(self.m2)
        l.append(self.m3)
        l.append(self.m4)

        assert len(l) == 4
        assert list(l.starting(2)) == [self.m2, self.m4]
        assert list(l.starting(3)) == [self.m3]
        assert list(l.ending(3)) == [self.m2]
        assert list(l.ending(4)) == [self.m3, self.m4]

        l.remove(self.m1)
        assert len(l) == 3
        assert len(l.starting(0)) == 0
        assert len(l.ending(2)) == 0

        l.clear()

        assert len(l) == 0
        assert len(l.starting(0)) == 0
        assert len(l.starting(2)) == 0
        assert len(l.starting(3)) == 0
        assert len(l.ending(2)) == 0
        assert len(l.ending(3)) == 0
        assert len(l.ending(4)) == 0

    def test_get_slices(self):
        l = Matches()
        l.append(self.m1)
        l.append(self.m2)
        l.append(self.m3)
        l.append(self.m4)

        slice_matches = l[1:3]

        assert isinstance(slice_matches, Matches)

        assert len(slice_matches) == 2
        assert slice_matches[0] == self.m2
        assert slice_matches[1] == self.m3

    def test_remove_slices(self):
        l = Matches()
        l.append(self.m1)
        l.append(self.m2)
        l.append(self.m3)
        l.append(self.m4)

        del l[1:3]

        assert len(l) == 2
        assert l[0] == self.m1
        assert l[1] == self.m4

    def test_set_slices(self):
        l = Matches()
        l.append(self.m1)
        l.append(self.m2)
        l.append(self.m3)
        l.append(self.m4)

        l[1:3] = self.m1, self.m4

        assert len(l) == 4
        assert l[0] == self.m1
        assert l[1] == self.m1
        assert l[2] == self.m4
        assert l[3] == self.m4

    def test_set_index(self):
        l = Matches()
        l.append(self.m1)
        l.append(self.m2)
        l.append(self.m3)

        l[1] = self.m4

        assert len(l) == 3
        assert l[0] == self.m1
        assert l[1] == self.m4
        assert l[2] == self.m3

    def test_iterator_constructor(self):
        l = Matches([self.m1, self.m2, self.m3, self.m4])

        assert len(l) == 4
        assert list(l.starting(0)) == [self.m1]
        assert list(l.ending(2)) == [self.m1]
        assert list(l.starting(2)) == [self.m2, self.m4]
        assert list(l.starting(3)) == [self.m3]
        assert list(l.ending(3)) == [self.m2]
        assert list(l.ending(4)) == [self.m3, self.m4]

    def test_constructor(self):
        l = Matches(self.m1, self.m2, self.m3, self.m4)

        assert len(l) == 4
        assert list(l.starting(0)) == [self.m1]
        assert list(l.ending(2)) == [self.m1]
        assert list(l.starting(2)) == [self.m2, self.m4]
        assert list(l.starting(3)) == [self.m3]
        assert list(l.ending(3)) == [self.m2]
        assert list(l.ending(4)) == [self.m3, self.m4]


class TestMatchFunctions:
    def test_group_neighbors(self):
        input_string = "abc.def._._.ghi.klm.nop.qrs.tuv.wyx.z"

        matches = StringPattern("abc", "def", "ghi", "nop", "qrs.tuv", "z").matches(input_string)
        matches_groups = list(group_neighbors(Matches(matches), input_string, "._"))

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

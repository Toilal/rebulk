#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

import pytest
import six

from ..match import Match, Matches
from ..pattern import StringPattern, RePattern


class TestMatchClass(object):
    pattern = StringPattern("test")

    def test_repr(self):
        match1 = Match(self.pattern, 1, 3, value="es")

        assert repr(match1) == '<es:(1, 3)>'

    def test_equality(self):
        match1 = Match(self.pattern, 1, 3, value="es")
        match2 = Match(self.pattern, 1, 3, value="es")

        other = object()

        assert hash(match1) == hash(match2)
        assert hash(match1) != hash(other)

        assert match1 == match2
        assert not match1 == other

    def test_inequality(self):
        match1 = Match(self.pattern, 0, 2, value="te")
        match2 = Match(self.pattern, 2, 4, value="st")
        match3 = Match(self.pattern, 0, 2, value="other")

        other = object()

        assert hash(match1) != hash(match2)
        assert hash(match1) != hash(match3)

        assert match1 != other
        assert match1 != match2
        assert match1 != match3

    def test_length(self):
        match1 = Match(self.pattern, 0, 4, value="test")
        match2 = Match(self.pattern, 0, 2, value="spanIsUsed")

        assert len(match1) == 4
        assert len(match2) == 2

    def test_compare(self):
        match1 = Match(self.pattern, 0, 2, value="te")
        match2 = Match(self.pattern, 2, 4, value="st")

        other = object()

        assert match1 < match2
        assert match1 <= match2

        assert match2 > match1
        assert match2 >= match1

        if six.PY3:
            with pytest.raises(TypeError):
                match1 < other

            with pytest.raises(TypeError):
                match1 <= other

            with pytest.raises(TypeError):
                match1 > other

            with pytest.raises(TypeError):
                match1 >= other
        else:
            assert match1 < other
            assert match1 <= other
            assert not match1 > other
            assert not match1 >= other


class TestMatchesClass(object):
    match1 = Match(StringPattern("te"), 0, 2, value="te", name="start")
    match2 = Match(StringPattern("s"), 2, 3, value="s", tags="tag1")
    match3 = Match(StringPattern("t"), 3, 4, value="t", tags=["tag1", "tag2"])
    match4 = Match(StringPattern("st"), 2, 4, value="st", name="end")

    def test_tag(self):
        matches = Matches()
        matches.append(self.match1)
        matches.append(self.match2)
        matches.append(self.match3)
        matches.append(self.match4)

        tag1 = matches.tagged("tag1")
        assert len(tag1) == 2
        assert tag1[0] == self.match2
        assert tag1[1] == self.match3

        tag2 = matches.tagged("tag2")
        assert len(tag2) == 1
        assert tag2[0] == self.match3

        start = matches.named("start")
        assert len(start) == 1
        assert start[0] == self.match1

        end = matches.named("end")
        assert len(end) == 1
        assert end[0] == self.match4

    def test_base(self):
        matches = Matches()
        matches.append(self.match1)

        assert len(matches) == 1
        assert repr(matches) == repr([self.match1])
        assert list(matches.starting(0)) == [self.match1]
        assert list(matches.ending(2)) == [self.match1]

        matches.append(self.match2)
        matches.append(self.match3)
        matches.append(self.match4)

        assert len(matches) == 4
        assert list(matches.starting(2)) == [self.match2, self.match4]
        assert list(matches.starting(3)) == [self.match3]
        assert list(matches.ending(3)) == [self.match2]
        assert list(matches.ending(4)) == [self.match3, self.match4]

        matches.remove(self.match1)
        assert len(matches) == 3
        assert len(matches.starting(0)) == 0
        assert len(matches.ending(2)) == 0

        matches.clear()

        assert len(matches) == 0
        assert len(matches.starting(0)) == 0
        assert len(matches.starting(2)) == 0
        assert len(matches.starting(3)) == 0
        assert len(matches.ending(2)) == 0
        assert len(matches.ending(3)) == 0
        assert len(matches.ending(4)) == 0

    def test_get_slices(self):
        matches = Matches()
        matches.append(self.match1)
        matches.append(self.match2)
        matches.append(self.match3)
        matches.append(self.match4)

        slice_matches = matches[1:3]

        assert isinstance(slice_matches, Matches)

        assert len(slice_matches) == 2
        assert slice_matches[0] == self.match2
        assert slice_matches[1] == self.match3

    def test_remove_slices(self):
        matches = Matches()
        matches.append(self.match1)
        matches.append(self.match2)
        matches.append(self.match3)
        matches.append(self.match4)

        del matches[1:3]

        assert len(matches) == 2
        assert matches[0] == self.match1
        assert matches[1] == self.match4

    def test_set_slices(self):
        matches = Matches()
        matches.append(self.match1)
        matches.append(self.match2)
        matches.append(self.match3)
        matches.append(self.match4)

        matches[1:3] = self.match1, self.match4

        assert len(matches) == 4
        assert matches[0] == self.match1
        assert matches[1] == self.match1
        assert matches[2] == self.match4
        assert matches[3] == self.match4

    def test_set_index(self):
        matches = Matches()
        matches.append(self.match1)
        matches.append(self.match2)
        matches.append(self.match3)

        matches[1] = self.match4

        assert len(matches) == 3
        assert matches[0] == self.match1
        assert matches[1] == self.match4
        assert matches[2] == self.match3

    def test_iterator_constructor(self):
        matches = Matches([self.match1, self.match2, self.match3, self.match4])

        assert len(matches) == 4
        assert list(matches.starting(0)) == [self.match1]
        assert list(matches.ending(2)) == [self.match1]
        assert list(matches.starting(2)) == [self.match2, self.match4]
        assert list(matches.starting(3)) == [self.match3]
        assert list(matches.ending(3)) == [self.match2]
        assert list(matches.ending(4)) == [self.match3, self.match4]

    def test_constructor(self):
        matches = Matches(self.match1, self.match2, self.match3, self.match4)

        assert len(matches) == 4
        assert list(matches.starting(0)) == [self.match1]
        assert list(matches.ending(2)) == [self.match1]
        assert list(matches.starting(2)) == [self.match2, self.match4]
        assert list(matches.starting(3)) == [self.match3]
        assert list(matches.ending(3)) == [self.match2]
        assert list(matches.ending(4)) == [self.match3, self.match4]


class TestMaches(object):
    def test_filters(self):
        input_string = "One Two Three"

        matches = Matches()

        matches.extend(StringPattern("One", name="1-str", tags=["One", "str"]).matches(input_string))
        matches.extend(RePattern("One", name="1-re", tags=["One", "re"]).matches(input_string))
        matches.extend(StringPattern("Two", name="2-str", tags=["Two", "str"]).matches(input_string))
        matches.extend(RePattern("Two", name="2-re", tags=["Two", "re"]).matches(input_string))
        matches.extend(StringPattern("Three", name="3-str", tags=["Three", "str"]).matches(input_string))
        matches.extend(RePattern("Three", name="3-re", tags=["Three", "re"]).matches(input_string))

        selection = matches.starting(0)
        assert len(selection) == 2

        selection = matches.starting(0, lambda m: "str" in m.tags)
        assert len(selection) == 1
        assert selection[0].pattern.name == "1-str"

        selection = matches.ending(7, predicate=lambda m: "str" in m.tags)
        assert len(selection) == 1
        assert selection[0].pattern.name == "2-str"

        selection = matches.previous(matches.named("2-str")[0])
        assert len(selection) == 2
        assert selection[0].pattern.name == "1-str"
        assert selection[1].pattern.name == "1-re"

        selection = matches.previous(matches.named("2-str", 0), lambda m: "str" in m.tags)
        assert len(selection) == 1
        assert selection[0].pattern.name == "1-str"

        selection = matches.next(matches.named("2-str", 0))
        assert len(selection) == 2
        assert selection[0].pattern.name == "3-str"
        assert selection[1].pattern.name == "3-re"

        selection = matches.next(matches.named("2-str", 0), index=0, predicate=lambda m: "re" in m.tags)
        assert selection is not None
        assert selection.pattern.name == "3-re"

        selection = matches.next(matches.named("2-str", index=0), lambda m: "re" in m.tags)
        assert len(selection) == 1
        assert selection[0].pattern.name == "3-re"

        selection = matches.named("2-str", lambda m: "re" in m.tags)
        assert len(selection) == 0

        selection = matches.named("2-re", lambda m: "re" in m.tags, 0)
        assert selection is not None
        assert selection.name == "2-re"

        selection = matches.named("2-re", lambda m: "re" in m.tags)
        assert len(selection) == 1
        assert selection[0].name == "2-re"

        selection = matches.named("2-re", lambda m: "re" in m.tags, index=1000)
        assert selection is None

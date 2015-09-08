#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from ..pattern import StringPattern, RePattern, FunctionalPattern
from ..match import Match


class TestStringPattern:
    """
    Tests for StringPattern matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_single(self):
        pattern = StringPattern("Celtic", label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].value == "Celtic"

    def test_no_match(self):
        pattern = StringPattern("Python")

        m2 = list(pattern.matches(self.input_string))
        assert not m2

    def test_multiple_patterns(self):
        pattern = StringPattern("playing", "annoyed", "Hebrew")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 3

        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (18, 25)
        assert matches[0].value == "playing"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (46, 53)
        assert matches[1].value == "annoyed"

        assert isinstance(matches[2], Match)
        assert matches[2].pattern == pattern
        assert matches[2].span == (88, 94)
        assert matches[2].value == "Hebrew"


class TestRePattern:
    """
    Tests for RePattern matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_single_compiled(self):
        pattern = RePattern(re.compile("Celt.?c"), label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].value == "Celtic"

    def test_single_string(self):
        pattern = RePattern("Celt.?c", label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].value == "Celtic"

    def test_single_kwargs(self):
        pattern = RePattern({"pattern": "celt.?c", "flags": re.IGNORECASE}, label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].value == "Celtic"

    def test_single_vargs(self):
        pattern = RePattern(("celt.?c", re.IGNORECASE), label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].value == "Celtic"

    def test_no_match(self):
        pattern = RePattern("abc.?def", label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 0

    def test_multiple_patterns(self):
        pattern = RePattern("pla.?ing", "ann.?yed", "Heb.?ew")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 3

        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (18, 25)
        assert matches[0].value == "playing"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (46, 53)
        assert matches[1].value == "annoyed"

        assert isinstance(matches[2], Match)
        assert matches[2].pattern == pattern
        assert matches[2].span == (88, 94)
        assert matches[2].value == "Hebrew"

    def test_unnamed_groups(self):
        pattern = RePattern("(Celt.?c)\s+(\w+)", label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 2

        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].name is None
        assert matches[0].value == "Celtic"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (35, 41)
        assert matches[1].name is None
        assert matches[1].value == "violin"

        assert matches[0].parent == matches[1].parent
        parent = matches[0].parent

        assert isinstance(parent, Match)
        assert parent.pattern == pattern
        assert parent.span == (28, 41)
        assert parent.name is None
        assert parent.value == "Celtic violin"

    def test_named_groups(self):
        pattern = RePattern("(?P<param1>Celt.?c)\s+(?P<param2>\w+)", label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 2

        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (28, 34)
        assert matches[0].name == "param1"
        assert matches[0].value == "Celtic"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (35, 41)
        assert matches[1].name == "param2"
        assert matches[1].value == "violin"

        assert matches[0].parent == matches[1].parent
        parent = matches[0].parent

        assert isinstance(parent, Match)
        assert parent.pattern == pattern
        assert parent.span == (28, 41)
        assert parent.name is None
        assert parent.value == "Celtic violin"


class TestFunctionalPattern:
    """
    Tests for FunctionalPattern matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_single_vargs(self):
        def func(input_string):
            i = input_string.find("fly")
            if i > -1:
                return i, i + len("fly"), "functional"

        pattern = FunctionalPattern(func, label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (14, 17)
        assert matches[0].name == "functional"
        assert matches[0].value == "fly"

    def test_single_kwargs(self):
        def func(input_string):
            i = input_string.find("fly")
            if i > -1:
                return {"start": i, "end": i + len("fly"), "name": "functional"}

        pattern = FunctionalPattern(func, label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (14, 17)
        assert matches[0].name == "functional"
        assert matches[0].value == "fly"

    def test_no_match(self):
        pattern = FunctionalPattern(lambda x: None, label="test")

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 0

    def test_multiple_patterns(self):
        def playing(input_string):
            i = input_string.find("playing")
            if i > -1:
                return i, i + len("playing")

        def annoyed(input_string):
            i = input_string.find("annoyed")
            if i > -1:
                return i, i + len("annoyed")

        def hebrew(input_string):
            i = input_string.find("Hebrew")
            if i > -1:
                return i, i + len("Hebrew")

        pattern = FunctionalPattern(playing, annoyed, hebrew)

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 3

        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (18, 25)
        assert matches[0].value == "playing"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (46, 53)
        assert matches[1].value == "annoyed"

        assert isinstance(matches[2], Match)
        assert matches[2].pattern == pattern
        assert matches[2].span == (88, 94)
        assert matches[2].value == "Hebrew"

class TestFormatter:
    """
    Tests for FunctionalPattern matching
    """

    input_string = "This string contains 1849 a number"

    def test_single_string(self):
        pattern = StringPattern("1849", formatters=lambda x: int(x)/2)

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (21, 25)
        assert matches[0].value == 1849/2

    def test_single_re_no_group(self):
        pattern = RePattern("\d+", formatters=lambda x: int(x)*2)

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (21, 25)
        assert matches[0].value == 1849*2

    def test_single_re_named_groups(self):
        pattern = RePattern("(?P<strParam>cont.?ins)\s+(?P<intParam>\d+)",
                            formatters={'intParam': lambda x: int(x)*2,
                                        'strParam': lambda x: "really " + x})

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 2
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (12, 20)
        assert matches[0].value == "really contains"

        assert isinstance(matches[1], Match)
        assert matches[1].pattern == pattern
        assert matches[1].span == (21, 25)
        assert matches[1].value == 1849*2

    def test_single_functional(self):
        def digit(input_string):
            i = input_string.find("1849")
            if i > -1:
                return i, i + len("1849")

        pattern = FunctionalPattern(digit, formatters=lambda x: int(x)*3)

        matches = list(pattern.matches(self.input_string))
        assert len(matches) == 1
        assert isinstance(matches[0], Match)
        assert matches[0].pattern == pattern
        assert matches[0].span == (21, 25)
        assert matches[0].value == 1849*3

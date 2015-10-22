#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from ..pattern import StringPattern, RePattern
from ..processors import conflict_prefer_longer
from rebulk.match import Matches


def test_conflict_prefer_longer():
    input_string = "abcdefghijklmnopqrstuvwxyz"

    pattern = StringPattern("ijklmn", "kl", "abcdef", "ab", "ef", "yz")
    matches = Matches(pattern.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)

    values = [x.value for x in processed_matches]

    assert values == ["ijklmn", "abcdef", "yz"]

    pattern = StringPattern("ijklmn", "jklmnopqrst")
    matches = Matches(pattern.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)

    values = [x.value for x in processed_matches]

    assert values == ["jklmnopqrst"]

    pattern = StringPattern("ijklmnopqrst", "jklmnopqrst")
    matches = Matches(pattern.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)

    values = [x.value for x in processed_matches]

    assert values == ["ijklmnopqrst"]

    input_string = "123456789"

    pattern = StringPattern("123", "456789")
    matches = Matches(pattern.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)

    values = [x.value for x in processed_matches]
    assert values == ["123", "456789"]

    pattern = StringPattern("123456", "789")
    matches = Matches(pattern.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)

    values = [x.value for x in processed_matches]
    assert values == ["123456", "789"]


def test_prefer_longer_parent():
    input_string = "xxx.1x02.xxx"

    re1 = RePattern("([0-9]+)x([0-9]+)", name='prefer', children=True, formatter=int)
    re2 = RePattern("x([0-9]+)", name='skip', children=True)

    matches = Matches(re1.matches(input_string))
    matches.extend(re2.matches(input_string))

    processed_matches = conflict_prefer_longer(matches)
    assert len(processed_matches) == 2
    assert processed_matches[0].value == 1
    assert processed_matches[1].value == 2



#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from ..pattern import StringPattern
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

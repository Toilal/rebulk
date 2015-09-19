#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from ..pattern import StringPattern
from ..filters import conflict_prefer_longer
from rebulk.match import Matches


def test_conflict_prefer_longer():
    input_string = "abcdefghijklmnopqrstuvwxyz"

    pattern = StringPattern("ijklmn", "kl", "abcdef", "ab", "ef", "yz")
    matches = Matches(pattern.matches(input_string))

    filtered_matches = conflict_prefer_longer(matches)

    values = [x.value for x in filtered_matches]

    assert values == ["ijklmn", "abcdef", "yz"]

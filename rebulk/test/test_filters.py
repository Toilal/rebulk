#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..pattern import StringPattern
from ..filters import conflict_prefer_longer
from ..runtime import Context


def test_conflict_prefer_longer():
    input_string = "abcdefghijklmnopqrstuvwxyz"

    pattern = StringPattern("ijklmn", "kl", "abcdef", "ab", "ef", "yz")
    matches = list(pattern.matches(input_string))

    filtered_matches = conflict_prefer_longer(matches, Context())

    values = [x.value for x in filtered_matches]

    assert values == ["ijklmn", "abcdef", "yz"]

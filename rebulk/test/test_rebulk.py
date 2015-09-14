#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import rebulk
from .. import Bucket
from rebulk.pattern import StringPattern, RePattern, FunctionalPattern


def test_rebulk_simple():
    bucket = Bucket()

    bucket.add_pattern(StringPattern("quick"))
    bucket.add_pattern(RePattern("f?x"))

    def func(input_string):
        i = input_string.find("over")
        if i > -1:
            return i, i + len("over")

    bucket.add_pattern(FunctionalPattern(func))

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk(bucket, input_string)
    assert len(matches) == 3

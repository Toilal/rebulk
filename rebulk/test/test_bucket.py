#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..pattern import StringPattern

import rebulk.bucket as bucket


class TestBucket:
    """
    Tests for Bucket matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_build(self):
        b = bucket.default()

        b.add_pattern(StringPattern("Abyssinian"), StringPattern("fly"), StringPattern("Celtic"),
                      StringPattern("Hebrew"))

        assert len(b.patterns) == 4
        assert b

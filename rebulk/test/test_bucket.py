#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from ..pattern import StringPattern

import rebulk.bucket as bucket


class TestBucket(object):
    """
    Tests for Bucket matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_build(self):
        buck = bucket.default()

        buck.add_pattern(StringPattern("Abyssinian"), StringPattern("fly"), StringPattern("Celtic"),
                         StringPattern("Hebrew"))

        assert len(buck.patterns) == 4
        assert buck

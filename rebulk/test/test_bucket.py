#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..pattern import StringPattern
from ..runtime import Response

import rebulk.bucket as bucket

class TestBucket:
    """
    Tests for Bucket matching
    """

    input_string = "An Abyssinian fly playing a Celtic violin was annoyed by trashy flags on " \
                   "which were the Hebrew letter qoph."

    def test_simple(self):
        b = bucket.default()

        b.add_pattern(StringPattern("Abyssinian"), StringPattern("fly"), StringPattern("Celtic"),
                      StringPattern("Hebrew"))

        response = b.response(self.input_string)

        assert isinstance(response, Response)
        assert len(response.matches) == 4

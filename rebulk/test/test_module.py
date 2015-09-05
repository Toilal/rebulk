#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import rebulk
from .. import Bucket

def test_rebulk():
    bucket = Bucket()

    input_string = "The quick brown fox jumps over the lazy dog"

    rebulk(bucket, input_string)

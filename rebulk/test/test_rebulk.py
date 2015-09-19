#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from .. import Rebulk


def test_rebulk_simple():
    rebulk = Rebulk()

    rebulk.string("quick")
    rebulk.regex("f.x")

    def func(input_string):
        i = input_string.find("over")
        if i > -1:
            return i, i + len("over")

    rebulk.functional(func)

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string)
    assert len(matches) == 3

    assert matches[0].value == "quick"
    assert matches[1].value == "fox"
    assert matches[2].value == "over"

def test_rebulk_defaults():
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = Rebulk().string("quick").string("own").regex("br.{2}n").matches(input_string)

    assert len(matches) == 2

    assert matches[0].value == "quick"
    assert matches[1].value == "brown"

def test_rebulk_no_filters():
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = Rebulk(default_filters=False).string("quick").string("own").regex("br.{2}n").matches(input_string)

    assert len(matches) == 3

    assert matches[0].value == "quick"
    assert matches[1].value == "own"
    assert matches[2].value == "brown"

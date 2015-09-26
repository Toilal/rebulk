#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring

from .. import Rebulk, Rule
import rebulk.test.rebulk_rules_module as rm


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


def test_rebulk_no_default():
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = Rebulk(default=False).string("quick").string("own").regex("br.{2}n").matches(input_string)

    assert len(matches) == 3

    assert matches[0].value == "quick"
    assert matches[1].value == "own"
    assert matches[2].value == "brown"


def test_rebulk_tags_names():
    rebulk = Rebulk()

    rebulk.string("quick", name="str", tags=["first", "other"])
    rebulk.regex("f.x", tags="other")

    def func(input_string):
        i = input_string.find("over")
        if i > -1:
            return i, i + len("over")

    rebulk.functional(func, name="fn")

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string)
    assert len(matches) == 3

    assert len(matches.named("str")) == 1
    assert len(matches.named("fn")) == 1
    assert len(matches.named("false")) == 0
    assert len(matches.tagged("false")) == 0
    assert len(matches.tagged("first")) == 1
    assert len(matches.tagged("other")) == 2


def test_rebulk_rules_1():
    rebulk = Rebulk()

    rebulk.regex(r'\d{4}', name="year")
    rebulk.rules(rm.RemoveAllButLastYear)

    matches = rebulk.matches("1984 keep only last 1968 entry 1982 case")
    assert len(matches) == 1
    assert matches[0].value == "1982"


def test_rebulk_rules_2():
    rebulk = Rebulk()

    rebulk.regex(r'\d{4}', name="year")
    rebulk.string(r'year', name="yearPrefix", private=True)
    rebulk.string(r'keep', name="yearSuffix", private=True)
    rebulk.rules(rm.PrefixedSuffixedYear)

    matches = rebulk.matches("Keep suffix 1984 keep prefixed year 1968 and remove the rest 1982")
    assert len(matches) == 2
    assert matches[0].value == "1984"
    assert matches[1].value == "1968"


def test_rebulk_rules_3():
    rebulk = Rebulk()

    rebulk.regex(r'\d{4}', name="year")
    rebulk.string(r'year', name="yearPrefix", private=True)
    rebulk.string(r'keep', name="yearSuffix", private=True)
    rebulk.rules(rm.PrefixedSuffixedYearNoLambda)

    matches = rebulk.matches("Keep suffix 1984 keep prefixed year 1968 and remove the rest 1982")
    assert len(matches) == 2
    assert matches[0].value == "1984"
    assert matches[1].value == "1968"


def test_rebulk_rules_4():
    class FirstOnlyRule(Rule):
        def when(self, matches, context):
            grabbed = matches.named("grabbed", 0)
            if grabbed and matches.previous(grabbed):
                return grabbed

        def then(self, matches, when_response, context):
            matches.remove(when_response)

    rebulk = Rebulk()

    rebulk.regex("This match (.*?)grabbed", name="grabbed")
    rebulk.regex("if it's (.*?)first match", private=True)

    rebulk.rules(FirstOnlyRule)

    matches = rebulk.matches("This match is grabbed only if it's the first match")
    assert len(matches) == 1
    assert matches[0].value == "This match is grabbed"

    matches = rebulk.matches("if it's NOT the first match, This match is NOT grabbed")
    assert len(matches) == 0


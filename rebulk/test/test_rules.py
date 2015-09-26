#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, invalid-name

from ..rules import Rules
from ..match import Matches, Match
from ..pattern import StringPattern

pattern = StringPattern("test")

from .rules_module import Rule1, Rule2, Rule3, Rule0, Rule1Disabled
import rebulk.test.rules_module as rm


def test_rule_priority():
    matches = Matches(Match(pattern, 1, 2))

    rules = Rules(Rule1, Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 0
    matches = Matches(Match(pattern, 1, 2))

    rules = Rules(Rule1(), Rule0)

    rules.execute_all_rules(matches, {})
    assert len(matches) == 1
    assert matches[0] == Match(pattern, 3, 4)


def test_rule_disabled():
    matches = Matches(Match(pattern, 1, 2))

    rules = Rules(Rule1Disabled(), Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 2
    assert matches[0] == Match(pattern, 1, 2)
    assert matches[1] == Match(pattern, 3, 4)


def test_rule_when():
    matches = Matches(Match(pattern, 1, 2))

    rules = Rules(Rule3())

    rules.execute_all_rules(matches, {'when': False})
    assert len(matches) == 1
    assert matches[0] == Match(pattern, 1, 2)

    matches = Matches(Match(pattern, 1, 2))

    rules.execute_all_rules(matches, {'when': True})
    assert len(matches) == 2
    assert matches[0] == Match(pattern, 1, 2)
    assert matches[1] == Match(pattern, 3, 4)


def test_rule_module():
    rules = Rules(rm)

    matches = Matches(Match(pattern, 1, 2))
    rules.execute_all_rules(matches, {})

    assert len(matches) == 1


def test_rule_repr():
    assert str(Rule0()) == "Rule0"
    assert str(Rule1()) == "Rule1"
    assert str(Rule2()) == "Rule2"
    assert str(Rule1Disabled()) == "Disabled Rule1"

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, invalid-name
from rebulk.test.default_rules_module import RuleRemove0, RuleAppend0, RuleAppend1, RuleRemove1

from ..rules import Rules
from ..match import Matches, Match

from .rules_module import Rule1, Rule2, Rule3, Rule0, Rule1Disabled
import rebulk.test.rules_module as rm


def test_rule_priority():
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1, Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 0
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1(), Rule0)

    rules.execute_all_rules(matches, {})
    assert len(matches) == 1
    assert matches[0] == Match(3, 4)


def test_rule_disabled():
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1Disabled(), Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 2
    assert matches[0] == Match(1, 2)
    assert matches[1] == Match(3, 4)


def test_rule_when():
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule3())

    rules.execute_all_rules(matches, {'when': False})
    assert len(matches) == 1
    assert matches[0] == Match(1, 2)

    matches = Matches([Match(1, 2)])

    rules.execute_all_rules(matches, {'when': True})
    assert len(matches) == 2
    assert matches[0] == Match(1, 2)
    assert matches[1] == Match(3, 4)


def test_default_rules():
    rules = Rules(RuleRemove0)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 0

    rules = Rules(RuleAppend0)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 2

    rules = Rules(RuleRemove1)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 0

    rules = Rules(RuleAppend1)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 2


def test_rule_module():
    rules = Rules(rm)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 1


def test_rule_repr():
    assert str(Rule0()) == "<Rule0>"
    assert str(Rule1()) == "<Rule1>"
    assert str(Rule2()) == "<Rule2>"
    assert str(Rule1Disabled()) == "<Disabled Rule1>"

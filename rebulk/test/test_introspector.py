#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Introspector tests
"""
# pylint: disable=no-self-use,pointless-statement,missing-docstring,protected-access,invalid-name
from .. import Rebulk
from .. import introspector
from .default_rules_module import RuleAppend2


def test_string_introspector():
    rebulk = Rebulk().string('One', 'Two', 'Three', name='first').string('1', '2', '3', name='second')

    introspected = introspector.introspect(rebulk, None)

    assert len(introspected.patterns) == 2

    first_properties = introspected.patterns[0].properties
    assert len(first_properties) == 1
    first_properties['first'] == ['One', 'Two', 'Three']

    second_properties = introspected.patterns[1].properties
    assert len(second_properties) == 1
    second_properties['second'] == ['1', '2', '3']

    properties = introspected.properties
    assert len(properties) == 2
    assert properties['first'] == first_properties['first']
    assert properties['second'] == second_properties['second']


def test_string_properties():
    rebulk = Rebulk()\
        .string('One', 'Two', 'Three', name='first', properties={'custom': ['One']})\
        .string('1', '2', '3', name='second', properties={'custom': [1]})

    introspected = introspector.introspect(rebulk, None)

    assert len(introspected.patterns) == 2
    assert len(introspected.rules) == 2

    first_properties = introspected.patterns[0].properties
    assert len(first_properties) == 1
    first_properties['custom'] == ['One']

    second_properties = introspected.patterns[1].properties
    assert len(second_properties) == 1
    second_properties['custom'] == [1]

    properties = introspected.properties
    assert len(properties) == 1
    assert properties['custom'] == ['One', 1]


def test_pattern_value():
    rebulk = Rebulk()\
        .regex('One', 'Two', 'Three', name='first', value="string") \
        .string('1', '2', '3', name='second', value="digit") \
        .string('4', '5', '6', name='third')

    introspected = introspector.introspect(rebulk, None)

    assert len(introspected.patterns) == 3
    assert len(introspected.rules) == 2

    first_properties = introspected.patterns[0].properties
    assert len(first_properties) == 1
    first_properties['first'] == ['string']

    second_properties = introspected.patterns[1].properties
    assert len(second_properties) == 1
    second_properties['second'] == ['digit']

    third_properties = introspected.patterns[2].properties
    assert len(third_properties) == 1
    third_properties['third'] == ['4', '5', '6']

    properties = introspected.properties
    assert len(properties) == 3
    assert properties['first'] == first_properties['first']
    assert properties['second'] == second_properties['second']
    assert properties['third'] == third_properties['third']


def test_rule_properties():
    rebulk = Rebulk().rules(RuleAppend2)

    introspected = introspector.introspect(rebulk, None)

    assert len(introspected.rules) == 3
    assert len(introspected.patterns) == 0

    rule_properties = introspected.rules[-1].properties
    assert len(rule_properties) == 1
    rule_properties['renamed'] == []

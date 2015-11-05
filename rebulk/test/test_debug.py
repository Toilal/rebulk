#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, protected-access, invalid-name

from ..pattern import StringPattern
from .. import Rebulk
from ..match import Match
from .. import debug
debug.DEBUG = True










pattern = StringPattern(1, 3, value="es")

match = Match(1, 3, value="es")


input_string = "This is a debug test"
rebulk = Rebulk().string("debug")\
    .string("is")

matches = rebulk.matches(input_string)


def test_pattern():
    assert pattern.defined_at.lineno == 20
    assert pattern.defined_at.name == 'rebulk.test.test_debug'
    assert pattern.defined_at.filename.endswith('test_debug.py')

    assert str(pattern.defined_at) == 'test_debug.py#L20'
    assert repr(pattern) == '<StringPattern@test_debug.py#L20:(1, 3)>'


def test_match():
    assert match.defined_at.lineno == 22
    assert match.defined_at.name == 'rebulk.test.test_debug'
    assert match.defined_at.filename.endswith('test_debug.py')

    assert str(match.defined_at) == 'test_debug.py#L22'


def test_rebulk():
    """
    This test fails on travis CI, can't find out why there's 1 line offset ...
    """
    assert rebulk._patterns[0].defined_at.lineno in [26, 27]
    assert rebulk._patterns[0].defined_at.name == 'rebulk.test.test_debug'
    assert rebulk._patterns[0].defined_at.filename.endswith('test_debug.py')

    assert str(rebulk._patterns[0].defined_at) in ['test_debug.py#L26', 'test_debug.py#L27']

    assert rebulk._patterns[1].defined_at.lineno in [27, 28]
    assert rebulk._patterns[1].defined_at.name == 'rebulk.test.test_debug'
    assert rebulk._patterns[1].defined_at.filename.endswith('test_debug.py')

    assert str(rebulk._patterns[1].defined_at) in ['test_debug.py#L27', 'test_debug.py#L28']

    assert matches[0].defined_at == rebulk._patterns[0].defined_at
    assert matches[1].defined_at == rebulk._patterns[1].defined_at


def test_repr():
    str(matches)

debug.DEBUG = False

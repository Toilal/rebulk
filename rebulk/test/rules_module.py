#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, invalid-name
from ..match import Match
from ..pattern import StringPattern
from ..rules import Rule


pattern = StringPattern("test")


class Rule3(Rule):
    priority = 3

    def when(self, matches, context):
        return context.get('when')

    def then(self, matches, when_response, context):
        assert when_response in [True, False]
        matches.append(Match(pattern, 3, 4))


class Rule2(Rule):
    priority = 2

    def when(self, matches, context):
        return True

    def then(self, matches, when_response, context):
        assert when_response
        matches.append(Match(pattern, 3, 4))


class Rule1(Rule):
    priority = 1

    def when(self, matches, context):
        return True

    def then(self, matches, when_response, context):
        assert when_response
        matches.clear()


class Rule0(Rule):
    def when(self, matches, context):
        return True

    def then(self, matches, when_response, context):
        assert when_response
        matches.append(Match(pattern, 3, 4))


class Rule1Disabled(Rule1):
    name = "Disabled Rule1"

    def enabled(self, context):
        return False

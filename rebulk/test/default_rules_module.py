#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, invalid-name
from ..match import Match
from ..rules import RemoveMatchRule, AppendMatchRule


class RuleRemove0(RemoveMatchRule):
    def when(self, matches, context):
        return matches[0]


class RuleAppend0(AppendMatchRule):
    def when(self, matches, context):
        return Match(5, 10)

class RuleRemove1(RemoveMatchRule):
    def when(self, matches, context):
        return [matches[0]]


class RuleAppend1(AppendMatchRule):
    def when(self, matches, context):
        return [Match(5, 10)]

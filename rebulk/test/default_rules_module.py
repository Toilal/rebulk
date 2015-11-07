#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, pointless-statement, missing-docstring, invalid-name
from ..match import Match
from ..rules import Rule, RemoveMatch, AppendMatch, RenameMatch


class RuleRemove0(Rule):
    consequence = RemoveMatch
    def when(self, matches, context):
        return matches[0]


class RuleAppend0(Rule):
    consequence = AppendMatch()
    def when(self, matches, context):
        return Match(5, 10)

class RuleRename0(Rule):
    consequence = [RenameMatch('renamed')]
    def when(self, matches, context):
        return [Match(5, 10, name="original")]

class RuleRemove1(Rule):
    consequence = [RemoveMatch()]
    def when(self, matches, context):
        return [matches[0]]

class RuleAppend1(Rule):
    consequence = [AppendMatch]
    def when(self, matches, context):
        return [Match(5, 10)]

class RuleRename1(Rule):
    consequence = RenameMatch('renamed')
    def when(self, matches, context):
        return [Match(5, 10, name="original")]

class RuleAppend2(Rule):
    consequence = [AppendMatch('renamed')]
    def when(self, matches, context):
        return [Match(5, 10)]

class RuleRename2(Rule):
    consequence = RenameMatch('renamed')
    def when(self, matches, context):
        return Match(5, 10, name="original")

class RuleAppend3(Rule):
    consequence = AppendMatch('renamed')
    def when(self, matches, context):
        return [Match(5, 10)]

class RuleRename3(Rule):
    consequence = [RenameMatch('renamed')]
    def when(self, matches, context):
        return Match(5, 10, name="original")


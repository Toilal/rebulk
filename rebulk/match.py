#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict

class Match:
    def __init__(self, pattern, start, end, name=None, parent=None, value=None):
        self.pattern = pattern
        self.start = start
        self.end = end
        self.name = name
        self.parent = parent
        self.children = []
        self.value = value

    @property
    def span(self):
        return self.start, self.end

    def __len__(self):
        return self.end - self.start

    def __hash__(self):
        return hash(Match) + hash(self.start) + hash(self.end) + hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, Match):
            return False
        return self.span == other.span and self.value == other.value

    def __repr__(self):
        return "%s<span=%s, value=\'%s\'>" % (self.__class__.__name__, self.span, self.value)

def start_end_hash(matches):
    """
    Computes a tuple(dict, dict) containing (start, end) hash for each match.

    :param matches:
    :type matches: __generator[Match]
    :return:
    :rtype: tuple(dict, dict)
    """

    start_dict, end_dict = defaultdict(set), defaultdict(set)
    for match in matches:
        start_dict[match.start].add(match)
        end_dict[match.end].add(match)
    return start_dict, end_dict

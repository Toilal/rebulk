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
        if isinstance(other, Match):
            return self.span == other.span and self.value == other.value
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Match):
            return self.span != other.span or self.value != other.value
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Match):
            return self.span < other.span
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Match):
            return self.span > other.span
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, Match):
            return self.span <= other.span
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Match):
            return self.span >= other.span
        return NotImplemented

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

def group_neighbors(matches, input_string, ignore_chars):
    """

    :param matches:
    :type matches: iterable[Match]
    :param input_string:
    :type input_string:
    :param ignore_chars:
    :type ignore_chars:
    :return:
    :rtype:
    """
    starts, ends = start_end_hash(matches)

    matches_at_position = []

    current_group = []
    ret = []

    for i in range(len(input_string)):
        matches_starting = starts[i]
        matches_ended = ends[i]

        matches_at_position.extend(matches_starting)
        matches_at_position = [m for m in matches_at_position if m not in matches_ended]

        ignoring = input_string[i] in ignore_chars

        if current_group and not matches_at_position and not ignoring:
            ret.append(current_group)
            current_group = []
        current_group.extend(matches_starting)

    if current_group:
        ret.append(current_group)

    return ret

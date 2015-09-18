#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict, MutableSequence
import six

from .ordered_set import OrderedSet


class Matches(MutableSequence):
    """
    A custom list[Match] that automatically maintains start, end hashes
    """

    def __init__(self, *matches):
        self._delegate = []
        self._start_dict = defaultdict(OrderedSet)
        self._end_dict = defaultdict(OrderedSet)
        if matches:
            if len(matches) == 1:
                try:
                    iterator = iter(matches)
                    self.extend(next(iterator))
                    return
                except TypeError:  # pragma: no cover
                    pass
            self.extend(matches)

    def _add_match(self, match):
        self._start_dict[match.start].add(match)
        self._end_dict[match.end].add(match)

    def _remove_match(self, match):
        self._start_dict[match.start].remove(match)
        self._end_dict[match.end].remove(match)

    def starting(self, start):
        return self._start_dict[start]

    def ending(self, end):
        return self._end_dict[end]

    if six.PY2:  # pragma: no cover
        def clear(self):
            """
            Python 3 backport
            """
            del self[:]

    def __len__(self):
        return len(self._delegate)

    def __getitem__(self, index):
        ret = self._delegate[index]
        if isinstance(ret, list):
            return Matches(ret)
        return ret

    def __setitem__(self, index, match):
        self._delegate[index] = match
        if isinstance(index, slice):
            for match_item in match:
                self._add_match(match_item)
            return
        self._add_match(match)

    def __delitem__(self, index):
        match = self._delegate[index]
        del self._delegate[index]
        if isinstance(match, list):
            # if index is a slice, we has a match list
            for match_item in match:
                self._remove_match(match_item)
        else:
            self._remove_match(match)

    def insert(self, index, match):
        self._delegate.insert(index, match)
        self._add_match(match)


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


def group_neighbors(matches, input_string, ignore_chars):
    """

    :param matches:
    :type matches: Matches
    :param input_string:
    :type input_string:
    :param ignore_chars:
    :type ignore_chars:
    :return:
    :rtype:
    """
    matches_at_position = []

    current_group = []

    for i in range(len(input_string)):
        matches_starting = matches.starting(i)
        matches_ended = matches.ending(i)

        matches_at_position.extend(matches_starting)
        matches_at_position = [m for m in matches_at_position if m not in matches_ended]

        ignoring = input_string[i] in ignore_chars

        if current_group and not matches_at_position and not ignoring:
            yield current_group
            current_group = []
        current_group.extend(matches_starting)

    if current_group:
        yield current_group

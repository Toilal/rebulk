#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes and functions related to matches
"""
from collections import defaultdict, MutableSequence
import six

from .ordered_set import OrderedSet
from .loose import ensure_list


class Matches(MutableSequence):
    """
    A custom list[Match] that automatically maintains name, tag, start and end lookup structures.
    """

    def __init__(self, *matches):
        self._delegate = []
        self._name_dict = defaultdict(OrderedSet)
        self._tag_dict = defaultdict(OrderedSet)
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
        """
        Add a match
        :param match:
        :type match: Match
        """
        if match.name:
            self._name_dict[match.name].add(match)
        for tag in match.tags:
            self._tag_dict[tag].add(match)
        self._start_dict[match.start].add(match)
        self._end_dict[match.end].add(match)

    def _remove_match(self, match):
        """
        Remove a match
        :param match:
        :type match: Match
        """
        if match.name:
            self._name_dict[match.name].remove(match)
        for tag in match.tags:
            self._tag_dict[tag].remove(match)
        self._start_dict[match.start].remove(match)
        self._end_dict[match.end].remove(match)

    def named(self, name):
        """
        Retrieves a set of Match objects that have the given name.
        :param name:
        :type name: str
        :return: set of matches
        :rtype: set[Match]
        """
        return self._name_dict[name]

    def tagged(self, tag):
        """
        Retrieves a set of Match objects that have the given tag defined.
        :param tag:
        :type tag: str
        :return: set of matches
        :rtype: set[Match]
        """
        return self._tag_dict[tag]

    def starting(self, start):
        """
        Retrieves a set of Match objects that starts at given index.
        :param start: the starting index
        :type start: int
        :return: set of matches
        :rtype: set[Match]
        """
        return self._start_dict[start]

    def ending(self, end):
        """
        Retrieves a set of Match objects that ends at given index.
        :param end: the ending index
        :type end: int
        :return: set of matches
        :rtype: set[Match]
        """
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

    def __repr__(self):
        return self._delegate.__repr__()

    def insert(self, index, match):
        self._delegate.insert(index, match)
        self._add_match(match)


class Match(object):
    """
    Object storing values related to a single match
    """
    def __init__(self, pattern, start, end, value=None, name=None, tags=None, parent=None):
        self.pattern = pattern
        self.start = start
        self.end = end
        self.name = name
        self.value = value
        self.tags = ensure_list(tags)
        self.parent = parent
        self.children = []

    @property
    def span(self):
        """
        2-tuple with start and end indices of the match
        """
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
        return "<%s:%s>" % (self.value, self.span)


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

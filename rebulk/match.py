#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Classes and functions related to matches
"""
from collections import defaultdict, MutableSequence
import six

#from .ordered_set import OrderedSet
from .loose import ensure_list, filter_index


class MatchesDict(dict):
    """
    A custom dict with matches property.
    """
    def __init__(self):
        super(MatchesDict, self).__init__()
        self.matches = defaultdict(list)


class _BaseMatches(MutableSequence):
    """
    A custom list[Match] that automatically maintains name, tag, start and end lookup structures.
    """
    _base = list  # OrderedSet
    _base_add = _base.append   # OrderedSet.add
    _base_remove = _base.remove  # OrderedSet.remove

    def __init__(self, matches=None, input_string=None):
        self.input_string = input_string
        self.max_end = 0
        self._delegate = []
        self._name_dict = defaultdict(_BaseMatches._base)
        self._tag_dict = defaultdict(_BaseMatches._base)
        self._start_dict = defaultdict(_BaseMatches._base)
        self._end_dict = defaultdict(_BaseMatches._base)
        if matches:
            self.extend(matches)

    def _add_match(self, match):
        """
        Add a match
        :param match:
        :type match: Match
        """
        if match.name:
            _BaseMatches._base_add(self._name_dict[match.name], (match))
        for tag in match.tags:
            _BaseMatches._base_add(self._tag_dict[tag], match)
        _BaseMatches._base_add(self._start_dict[match.start], match)
        _BaseMatches._base_add(self._end_dict[match.end], match)
        if match.end > self.max_end:
            self.max_end = match.end

    def _remove_match(self, match):
        """
        Remove a match
        :param match:
        :type match: Match
        """
        if match.name:
            _BaseMatches._base_remove(self._name_dict[match.name], match)
        for tag in match.tags:
            _BaseMatches._base_remove(self._tag_dict[tag], match)
        _BaseMatches._base_remove(self._start_dict[match.start], match)
        _BaseMatches._base_remove(self._end_dict[match.end], match)
        if match.end >= self.max_end and not self._end_dict[match.end]:
            self.max_end = max(self._end_dict.keys())

    def previous(self, match, predicate=None, index=None):
        """
        Retrieves the nearest previous matches.
        :param match:
        :type match:
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return:
        :rtype:
        """
        current = match.start
        while current > -1:
            current -= 1
            previous_matches = self.ending(current)
            if previous_matches:
                return filter_index(previous_matches, predicate, index)
        return filter_index(_BaseMatches._base(), predicate, index)

    def next(self, match, predicate=None, index=None):
        """
        Retrieves the nearest next matches.
        :param match:
        :type match:
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return:
        :rtype:
        """
        current = match.start
        while current <= self.max_end:
            current += 1
            next_matches = self.starting(current)
            if next_matches:
                return filter_index(next_matches, predicate, index)
        return filter_index(_BaseMatches._base(), predicate, index)

    def named(self, name, predicate=None, index=None):
        """
        Retrieves a set of Match objects that have the given name.
        :param name:
        :type name: str
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return: set of matches
        :rtype: set[Match]
        """
        return filter_index(self._name_dict[name], predicate, index)

    def tagged(self, tag, predicate=None, index=None):
        """
        Retrieves a set of Match objects that have the given tag defined.
        :param tag:
        :type tag: str
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return: set of matches
        :rtype: set[Match]
        """
        return filter_index(self._tag_dict[tag], predicate, index)

    def starting(self, start, predicate=None, index=None):
        """
        Retrieves a set of Match objects that starts at given index.
        :param start: the starting index
        :type start: int
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return: set of matches
        :rtype: set[Match]
        """
        return filter_index(self._start_dict[start], predicate, index)

    def ending(self, end, predicate=None, index=None):
        """
        Retrieves a set of Match objects that ends at given index.
        :param end: the ending index
        :type end: int
        :param predicate:
        :type predicate:
        :return: set of matches
        :rtype: set[Match]
        """
        return filter_index(self._end_dict[end], predicate, index)

    def range(self, start=0, end=None, predicate=None, index=None):
        """
        Retrieves a set of Match objects that are available in given range
        :param start: the starting index
        :type start: int
        :param end: the ending index
        :type end: int
        :param predicate:
        :type predicate:
        :param index:
        :type index: int
        :return: set of matches
        :rtype: set[Match]
        """
        if end is None:
            end = self.max_end
        ret = []
        for match in self:
            if match.start < end and match.end > start:
                ret.append(match)
        return filter_index(ret, predicate, index)

    def _close_hole(self, hole_match, end, formatter=None):
        """
        Close a hole match by setting it's value using provided formatter.
        :param hole_match:
        :type hole_match:
        :param end:
        :type end:
        :param formatter:
        :type formatter:
        :return:
        :rtype:
        """
        hole_match.end = end
        hole_match.value = self.input_string[hole_match.start:hole_match.end]
        if formatter:
            hole_match.value = formatter(hole_match.value)

    def holes(self, start=0, end=None, formatter=None, predicate=None, index=None):  # pylint: disable=too-many-branches
        """
        Retrieves a set of Match objects that are not defined in given range.
        :param start:
        :type start:
        :param end:
        :type end:
        :param formatter:
        :type formatter:
        :param predicate:
        :type predicate:
        :param index:
        :type index:
        :return:
        :rtype:
        """
        if end is None:
            end = self.max_end
        ret = []
        current = []
        hole = False
        rindex = start
        loop_start = start

        if start > 0:
            # go the the previous starting element ...
            for lindex in reversed(range(0, start)):
                if self.starting(lindex):
                    loop_start = lindex
                    break

        for rindex in range(loop_start, end):
            for starting in self.starting(rindex):
                if starting not in current:
                    current.append(starting)
            for ending in self.ending(rindex):
                if ending in current:
                    current.remove(ending)
            if not current and not hole:
                # Open a new hole match
                hole = True
                ret.append(Match(max(rindex, start), None, input_string=self.input_string))
            elif current and hole:
                # Close current hole match
                hole = False
                self._close_hole(ret[-1], rindex, formatter)

        if ret and hole:
            lindex = rindex

            # go the the next starting element ...
            for rindex in range(lindex, self.max_end):
                if self.starting(rindex):
                    break

            self._close_hole(ret[-1], min(rindex, end), formatter)
        return filter_index(ret, predicate, index)

    @property
    def names(self):
        """
        Retrieve all names.
        :return:
        """
        return self._name_dict.keys()

    @property
    def tags(self):
        """
        Retrieve all tags.
        :return:
        """
        return self._tag_dict.keys()

    def to_dict(self, details=False):
        """
        Converts matches to a dict object.
        :param details if True, values will be complete Match object, else it will be only string Match.value property
        :type details: bool
        :return:
        :rtype: dict
        """
        ret = MatchesDict()
        for match in self:
            value = match if details else match.value
            ret.matches[match.name].append(match)
            if match.name in ret.keys():
                if not isinstance(ret[match.name], list):
                    if ret[match.name] == value:
                        continue
                    ret[match.name] = [ret[match.name]]
                else:
                    if value in ret[match.name]:
                        continue
                ret[match.name].append(value)
            else:
                ret[match.name] = value
        return ret

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


class Matches(_BaseMatches):
    """
    A custom list[Match] that automatically maintains name, tag, start and end lookup structures.
    Dedicated for non markers matches, it contains a markers list.
    """
    def __init__(self, matches=None, input_string=None):
        self.markers = Markers()
        super(Matches, self).__init__(matches=matches, input_string=input_string)

    def _add_match(self, match):
        assert not match.marker, "A marker match should not be added to <Matches> object"
        super(Matches, self)._add_match(match)


class Markers(_BaseMatches):
    """
    A custom list[Match] that automatically maintains name, tag, start and end lookup structures.
    Dedicated to markers matches.
    """
    def __init__(self, matches=None, input_string=None):
        self._index_dict = defaultdict(Markers._base)
        super(Markers, self).__init__(matches=None, input_string=input_string)

    def _add_match(self, match):
        assert match.marker, "A non-marker match should not be added to <Markers> object"
        super(Markers, self)._add_match(match)
        for index in range(*match.span):
            Markers._base_add(self._index_dict[index], match)

    def _remove_match(self, match):
        for index in range(*match.span):
            Markers._base_remove(self._index_dict[index], match)

    def at_match(self, match, predicate=None, index=None):
        """
        Retrieves a list of markers from given match.
        """
        return self.at_span(match.span, predicate, index)

    def at_span(self, span, predicate=None, index=None):
        """
        Retrieves a list of markers from given (start, end) tuple.
        """
        starting = self._index_dict[span[0]]
        ending = self._index_dict[span[1]]

        merged = list(starting)
        for marker in ending:
            if marker not in merged:
                merged.append(marker)

        return filter_index(merged, predicate, index)

    def at_index(self, pos, predicate=None, index=None):
        """
        Retrieves a list of markers from given position
        """
        return filter_index(self._index_dict[pos], predicate, index)


class Match(object):
    """
    Object storing values related to a single match
    """
    def __init__(self, start, end, value=None, name=None, tags=None, marker=None, parent=None, private=None,
                 pattern=None, input_string=None):
        self.start = start
        self.end = end
        self.name = name
        self.value = value
        self.tags = ensure_list(tags)
        self.marker = marker
        self.parent = parent
        self.input_string = input_string
        self.pattern = pattern
        self.private = private
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

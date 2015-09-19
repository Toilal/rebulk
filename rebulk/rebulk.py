#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point functions and classes for Rebulk
"""
from .match import Matches

from .pattern import RePattern, StringPattern, FunctionalPattern

from .filters import conflict_prefer_longer
from .loose import call

class Rebulk(object):
    """
    Regular expression, string and function based patterns are declared in a Rebulk object with a consistent API.

    It contains a matches method to retrieve all sequence of all matches found by registered patterns.

    .. code-block:: python

        >>> from rebulk import Rebulk
        >>> rebulk = Rebulk().regex('qu\\w+').string('brown').functional(lambda s: (20, 25))
        >>> rebulk.matches("The quick brown fox jumps over the lazy dog")
        [<quick:(4, 9)>, <brown:(10, 15)>, <jumps:(20, 25)>]

    If multiple matches are found at the same position, the longer match is kept and shorters are dropped.

    .. code-block:: python

        >>> rebulk = Rebulk().string('la').string('lakers')
        >>> rebulk.matches("the lakers are from la") # la string from lakers won't match
        [<la:(20, 22)>, <lakers:(4, 10)>]

    Options can be given to patterns using keyword arguments.

    .. code-block:: python
        >>> import re
        >>> rebulk = Rebulk().regex('L[A-Z]', flags=re.IGNORECASE).regex('L[A-Z]KERS', flags=re.IGNORECASE)
        >>> rebulk.matches("The LoKeRs are from Lo")
        [<Lo:(20, 22)>, <LoKeRs:(4, 10)>]
    """

    def __init__(self, default_filters=True):
        self._patterns = []
        self._filters = []
        if default_filters:
            self.filter(*DEFAULT_FILTERS)

    def pattern(self, *pattern):
        """
        Add patterns objects

        :param pattern:
        :type pattern: rebulk.pattern.Pattern
        :return: self
        :rtype: Rebulk
        """
        self._patterns.extend(pattern)
        return self

    def regex(self, *pattern, **kwargs):
        """
        Add re pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        self.pattern(RePattern(*pattern, **kwargs))
        return self

    def string(self, *pattern, **kwargs):
        """
        Add string pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        self.pattern(StringPattern(*pattern, **kwargs))
        return self

    def functional(self, *pattern, **kwargs):
        """
        Add functional pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        self.pattern(FunctionalPattern(*pattern, **kwargs))
        return self

    def filter(self, *func):
        """
        Add a Match filter functions

        :param func:
        :type func: list[rebulk.match.Match] = function(list[rebulk.match.Match])
        """
        self._filters.extend(func)
        return self

    def matches(self, string):
        """
        Search for all matches with current configuration against input_string
        :param string: string to search into
        :type string: str
        :return: A custom list of matches
        :rtype: Matches
        """
        matches = Matches()
        context = {}

        for pattern in self._patterns:
            for match in pattern.matches(string):
                matches.append(match)

        for func in self._filters:
            matches = call(func, matches, context)

        return matches


DEFAULT_FILTERS = [conflict_prefer_longer]

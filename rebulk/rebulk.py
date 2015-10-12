#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point functions and classes for Rebulk
"""
from .match import Matches

from .pattern import RePattern, StringPattern, FunctionalPattern

from .processors import conflict_prefer_longer, remove_private
from .loose import call, set_defaults
from .utils import extend_safe
from .rules import Rules


class Rebulk(object):
    r"""
    Regular expression, string and function based patterns are declared in a ``Rebulk`` object. It use a fluent API to
    chain ``string``, ``regex``, and ``functional`` methods to define various patterns types.

    .. code-block:: python

        >>> from rebulk import Rebulk
        >>> bulk = Rebulk().string('brown').regex(r'qu\w+').functional(lambda s: (20, 25))

    When ``Rebulk`` object is fully configured, you can call ``matches`` method with an input string to retrieve all
    ``Match`` objects found by registered pattern.

    .. code-block:: python

        >>> bulk.matches("The quick brown fox jumps over the lazy dog")
        [<brown:(10, 15)>, <quick:(4, 9)>, <jumps:(20, 25)>]

    If multiple ``Match`` objects are found at the same position, only the longer one is kept.

    .. code-block:: python

        >>> bulk = Rebulk().string('lakers').string('la')
        >>> bulk.matches("the lakers are from la")
        [<lakers:(4, 10)>, <la:(20, 22)>]
    """

    def __init__(self, default=True):
        self._patterns = []
        self._processors = []
        self._post_processors = []
        if default:
            self.processor(*DEFAULT_PROCESSORS)
            self.post_processor(*DEFAULT_POST_PROCESSORS)
        self._rules = Rules()
        self._defaults = {}
        self._regex_defaults = {}
        self._string_defaults = {}
        self._functional_defaults = {}

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

    def defaults(self, **kwargs):
        """
        Define default keyword arguments for all patterns
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        self._defaults = kwargs
        return self

    def regex_defaults(self, **kwargs):
        """
        Define default keyword arguments for functional patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        self._regex_defaults = kwargs
        return self

    def regex(self, *pattern, **kwargs):
        """
        Add re pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        set_defaults(self._regex_defaults, kwargs)
        set_defaults(self._defaults, kwargs)
        self.pattern(RePattern(*pattern, **kwargs))
        return self

    def string_defaults(self, **kwargs):
        """
        Define default keyword arguments for string patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        self._string_defaults = kwargs
        return self

    def string(self, *pattern, **kwargs):
        """
        Add string pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        set_defaults(self._string_defaults, kwargs)
        set_defaults(self._defaults, kwargs)
        self.pattern(StringPattern(*pattern, **kwargs))
        return self

    def functional_defaults(self, **kwargs):
        """
        Define default keyword arguments for functional patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        self._functional_defaults = kwargs
        return self

    def functional(self, *pattern, **kwargs):
        """
        Add functional pattern

        :param pattern:
        :type pattern:
        :return: self
        :rtype: Rebulk
        """
        set_defaults(self._functional_defaults, kwargs)
        set_defaults(self._defaults, kwargs)
        self.pattern(FunctionalPattern(*pattern, **kwargs))
        return self

    def processor(self, *func):
        """
        Add matches processor function.

        Default processors can be found in rebulk.processors module.

        :param func:
        :type func: list[rebulk.match.Match] = function(list[rebulk.match.Match])
        """
        self._processors.extend(func)
        return self

    def post_processor(self, *func):
        """
        Add matches post_processor function.

        Default processors can be found in rebulk.processors module.

        :param func:
        :type func: list[rebulk.match.Match] = function(list[rebulk.match.Match])
        """
        self._post_processors.extend(func)
        return self

    def rules(self, *rules):
        """
        Add rules as a module, class or instance.
        :param rules:
        :type rules: list[Rule]
        :return:
        """
        self._rules.load(*rules)
        return self

    def rebulk(self, *rebulks):
        """
        Add all configuration from given Rebulk objects.
        :param rebulks:
        :type rebulks: Rebulk
        :return:
        """
        #pylint: disable=protected-access
        for rebulk in rebulks:
            extend_safe(self._patterns, rebulk._patterns)
            extend_safe(self._processors, rebulk._processors)
            extend_safe(self._post_processors, rebulk._post_processors)
            extend_safe(self._rules, rebulk._rules)
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
                if match.marker:
                    matches.markers.append(match)
                else:
                    matches.append(match)

        for func in self._processors:
            ret = call(func, matches, context)
            if isinstance(ret, Matches):
                matches = ret

        self._rules.execute_all_rules(matches, context)

        for func in self._post_processors:
            ret = call(func, matches, context)
            if isinstance(ret, Matches):
                matches = ret

        return matches


DEFAULT_PROCESSORS = [conflict_prefer_longer]
DEFAULT_POST_PROCESSORS = [remove_private]

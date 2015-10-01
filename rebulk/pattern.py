#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abstract pattern class definition along with various implementations (regexp, string, functional)
"""
# pylint: disable=super-init-not-called

from abc import ABCMeta, abstractmethod, abstractproperty
REGEX_AVAILABLE = None
try:
    import regex as re
    REGEX_AVAILABLE = True
except ImportError:  # pragma: no cover
    import re
    REGEX_AVAILABLE = False

import six

from .match import Match
from .utils import find_all
from .loose import call, ensure_list, ensure_dict


@six.add_metaclass(ABCMeta)
class Pattern(object):
    """
    Definition of a particular pattern to search for.
    """

    def __init__(self, name=None, tags=None, formatter=None, validator=None, private=False, marker=False):
        """
        :param name: Name of this pattern
        :type name: str
        :param tags: List of tags related to this pattern
        :type tags: list[str]
        :param formatter: dict (name, func) of formatter to use with this pattern. name is the match name to support,
        and func a function(input_string) that returns the formatted string. A single formatter function can also be
        passed as a shortcut for {None: formatter}. The returned formatted string with be set in Match.value property.
        :type formatter: dict[str, func] || func
        :param validator: dict (name, func) of validator to use with this pattern. name is the match name to support,
        and func a function(match) that returns the a boolean. A single validator function can also be
        passed as a shortcut for {None: validator}. If return value is False, match will be ignored.
        :param private: flag this pattern as beeing private.
        :type private: bool
        :param marker: flag this pattern as beeing a marker.
        :type private: bool
        :type formatter: dict[str, func] || func
        """
        self.name = name
        self.tags = ensure_list(tags)
        self._default_formatter = lambda x: x
        self.formatters = ensure_dict(formatter, self._default_formatter)
        self._default_validator = lambda match: True
        self.validators = ensure_dict(validator, self._default_validator)
        self.private = private
        self.marker = marker

    def matches(self, input_string):
        """
        Computes all matches for a given input

        :param input_string: the string to parse
        :type input_string: str
        :return: matches based on input_string for this pattern
        :rtype: iterator[Match]
        """
        for pattern in self.patterns:
            for match in self._match(pattern, input_string):
                if match.value is None:
                    value = input_string[match.start:match.end]
                    formatter = self.formatters.get(match.name, self._default_formatter)
                    value = formatter(value)
                    match.value = value
                validator = self.validators.get(match.name, self._default_validator)
                if not validator(match):
                    break
                validated = True
                for child in match.children:
                    if child.value is None:
                        value = input_string[child.start:child.end]
                        formatter = self.formatters.get(child.name, self._default_formatter)
                        value = formatter(value)
                        child.value = value
                    validator = self.validators.get(child.name, self._default_validator)
                    if not validator(child):
                        validated = False
                        break
                if validated:
                    yield match

    @abstractproperty
    def patterns(self):  # pragma: no cover
        """
        List of base patterns defined

        :return: A list of base patterns
        :rtype: list
        """
        pass

    @abstractmethod
    def _match(self, pattern, input_string):  # pragma: no cover
        """
        Computes all matches for a given pattern and input

        :param pattern: the pattern to use
        :param input_string: the string to parse
        :type input_string: str
        :return: matches based on input_string for this pattern
        :rtype: iterator[Match]
        """
        pass


class StringPattern(Pattern):
    """
    Definition of one or many strings to search for.
    """

    def __init__(self, *patterns, **kwargs):
        call(super(StringPattern, self).__init__, **kwargs)
        self._patterns = patterns
        self._kwargs = kwargs
        self._match_kwargs = _filter_match_kwargs(kwargs)

    @property
    def patterns(self):
        return self._patterns

    def _match(self, pattern, input_string):
        for index in call(find_all, input_string, pattern, **self._kwargs):
            yield call(Match, self, index, index + len(pattern), **self._match_kwargs)


class RePattern(Pattern):
    """
    Definition of one or many regular expression pattern to search for.
    """

    def __init__(self, *patterns, **kwargs):
        call(super(RePattern, self).__init__, **kwargs)
        self.repeated_captures = REGEX_AVAILABLE
        if 'repeated_captures' in kwargs:
            self.repeated_captures = kwargs.get('repeated_captures')
        if self.repeated_captures and not REGEX_AVAILABLE:  # pragma: no cover
            raise NotImplementedError("repeated_capture is available only with regex module.")
        self._kwargs = kwargs
        self._match_kwargs = _filter_match_kwargs(kwargs)
        self._children_match_kwargs = _filter_match_kwargs(kwargs, children=True)
        self._patterns = []
        for pattern in patterns:
            if isinstance(pattern, six.string_types):
                pattern = call(re.compile, pattern, **self._kwargs)
            elif isinstance(pattern, dict):
                pattern = re.compile(**pattern)
            elif hasattr(pattern, '__iter__'):
                pattern = re.compile(*pattern)
            self._patterns.append(pattern)

    @property
    def patterns(self):
        return self._patterns

    def _match(self, pattern, input_string):
        names = {v: k for k, v in pattern.groupindex.items()}
        for match_object in pattern.finditer(input_string):
            start = match_object.start()
            end = match_object.end()
            main_match = call(Match, self, start, end, **self._match_kwargs)

            if pattern.groups:
                for i in range(1, pattern.groups + 1):
                    name = names.get(i, None)
                    if self.repeated_captures:
                        for start, end in match_object.spans(i):
                            child_match = call(Match, self, start, end, name=name, parent=main_match,
                                               **self._children_match_kwargs)
                            main_match.children.append(child_match)
                    else:
                        start, end = match_object.span(i)
                        child_match = call(Match, self, start, end, name=name, parent=main_match,
                                           **self._children_match_kwargs)
                        main_match.children.append(child_match)

            yield main_match


class FunctionalPattern(Pattern):
    """
    Definition of one or many functional pattern to search for.
    """

    def __init__(self, *patterns, **kwargs):
        call(super(FunctionalPattern, self).__init__, **kwargs)
        self._patterns = patterns
        self._kwargs = kwargs
        self._match_kwargs = _filter_match_kwargs(kwargs)

    @property
    def patterns(self):
        return self._patterns

    def _match(self, pattern, input_string):
        ret = call(pattern, input_string, **self._kwargs)
        if ret:
            if isinstance(ret, dict):
                options = ret
                if self._match_kwargs:
                    options = self._match_kwargs.copy()
                    options.update(ret)
                yield call(Match, self, **options)
            else:
                yield call(Match, self, *ret, **self._match_kwargs)


def _filter_match_kwargs(kwargs, children=False):
    """
    Filters out kwargs for Match construction

    :param kwargs:
    :type kwargs: dict
    :param children:
    :type children: Flag to filter children matches
    :return: A filtered dict
    :rtype: dict
    """
    kwargs = kwargs.copy()
    for key in ('pattern', 'start', 'end', 'parent'):
        if key in kwargs:
            del kwargs[key]
    if children:
        for key in ('name',):
            if key in kwargs:
                del kwargs[key]
    return kwargs

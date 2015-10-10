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
from .utils import find_all, is_iterable
from .loose import call, ensure_list, ensure_dict


@six.add_metaclass(ABCMeta)
class Pattern(object):
    """
    Definition of a particular pattern to search for.
    """

    def __init__(self, name=None, tags=None, formatter=None, validator=None, children=False, private=False,
                 marker=False, format_all=False, validate_all=False):
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
        :param children: generates children instead of parent
        :type children: bool
        :param private: flag this pattern as beeing private.
        :type private: bool
        :param marker: flag this pattern as beeing a marker.
        :type private: bool
        :param format_all if True, pattern will format every match in the hierarchy (even match not yield).
        :type format_all: bool
        :param validate_all if True, pattern will validate every match in the hierarchy (even match not yield).
        :type validate_all: bool

        """
        self.name = name
        self.tags = ensure_list(tags)
        self.formatters, self._default_formatter = ensure_dict(formatter, lambda x: x)
        self.validators, self._default_validator = ensure_dict(validator, lambda match: True)
        self.children = children
        self.private = private
        self.marker = marker
        self.format_all = format_all
        self.validate_all = validate_all

    def _yield_children(self, match):
        """
        Does this mat
        :param match:
        :type match:
        :return:
        :rtype:
        """
        return self.children and match.children

    def _match_parent(self, match, input_string, yield_children):
        """
        Handle a parent match
        :param match:
        :type match:
        :param input_string:
        :type input_string:
        :param yield_children:
        :type yield_children:
        :return:
        :rtype:
        """
        if match.value is None:
            value = input_string[match.start:match.end]
            if not yield_children or self.format_all:
                formatter = self.formatters.get(match.name, self._default_formatter)
                value = formatter(value)
            match.value = value
        if not yield_children or self.validate_all:
            validator = self.validators.get(match.name, self._default_validator)
            if not validator(match):
                return False
        return True

    def _match_child(self, child, input_string, yield_children):
        """
        Handle a children match
        :param child:
        :type child:
        :param input_string:
        :type input_string:
        :param yield_children:
        :type yield_children:
        :return:
        :rtype:
        """
        if child.value is None:
            value = input_string[child.start:child.end]
            if yield_children or self.format_all:
                formatter = self.formatters.get(child.name, self._default_formatter)
                value = formatter(value)
            child.value = value
        if yield_children or self.validate_all:
            validator = self.validators.get(child.name, self._default_validator)
            if not validator(child):
                return False
        return True

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
                yield_children = self._yield_children(match)
                if not self._match_parent(match, input_string, yield_children):
                    break
                validated = True
                for child in match.children:
                    if not self._match_child(child, input_string, yield_children):
                        validated = False
                        break
                if validated:
                    if yield_children:
                        for child in match.children:
                            yield child
                    else:
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
            yield call(Match, index, index + len(pattern), pattern=self, input_string=input_string,
                       **self._match_kwargs)


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
        self.abbreviations = kwargs.get('abbreviations', [])
        self._kwargs = kwargs
        self._match_kwargs = _filter_match_kwargs(kwargs)
        self._children_match_kwargs = _filter_match_kwargs(kwargs, children=True)
        self._patterns = []
        for pattern in patterns:
            if isinstance(pattern, six.string_types):
                if self.abbreviations and pattern:
                    for key, replacement in self.abbreviations:
                        pattern = pattern.replace(key, replacement)
                pattern = call(re.compile, pattern, **self._kwargs)
            elif isinstance(pattern, dict):
                if self.abbreviations and 'pattern' in pattern:
                    for key, replacement in self.abbreviations:
                        pattern['pattern'] = pattern['pattern'].replace(key, replacement)
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
            main_match = call(Match, start, end, pattern=self, input_string=input_string, **self._match_kwargs)

            if pattern.groups:
                for i in range(1, pattern.groups + 1):
                    name = names.get(i, main_match.name)
                    if self.repeated_captures:
                        for start, end in match_object.spans(i):
                            child_match = call(Match, start, end, name=name, parent=main_match, pattern=self,
                                               input_string=input_string, **self._children_match_kwargs)
                            main_match.children.append(child_match)
                    else:
                        start, end = match_object.span(i)
                        child_match = call(Match, start, end, name=name, parent=main_match, pattern=self,
                                           input_string=input_string, **self._children_match_kwargs)
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
            if not is_iterable(ret) or isinstance(ret, dict) or is_iterable(ret) and isinstance(ret[0], int):
                args_iterable = [ret]
            else:
                args_iterable = ret
            for args in args_iterable:
                if isinstance(args, Match):
                    args.input_string = input_string
                    args.pattern = self
                    yield args
                elif isinstance(args, dict):
                    options = args
                    if self._match_kwargs:
                        options = self._match_kwargs.copy()
                        options.update(args)
                    yield call(Match, pattern=self, input_string=input_string, **options)
                else:
                    yield call(Match, *args, pattern=self, input_string=input_string, **self._match_kwargs)


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

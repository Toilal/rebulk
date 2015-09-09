#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .runtime import Request

from .filters import conflict_prefer_longer


class Bucket:
    """
    A bucket is a container of predefined patterns and filters
    """
    patterns = []
    filters = []

    def add_pattern(self, *pattern):
        """
        Add a pattern object to this Bucket.

        :param pattern:
        :type pattern: rebulk.pattern.Pattern
        """
        self.patterns.extend(pattern)

    def add_match_filter(self, *func):
        """
        Add a Match filter function to this Bucket.

        :param func:
        :type func: list[rebulk.match.Match] = function(list[rebulk.match.Match])
        """
        self.filters.extend(func)

    def response(self, input_string):
        """

        :param input_string:
        :type input_string: str
        :return:
        :rtype: rebulk.runtime.Response
        """
        return Request(self, input_string).execute()

def default():
    b = Bucket()
    b.add_match_filter(conflict_prefer_longer)
    return b

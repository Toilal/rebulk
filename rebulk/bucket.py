#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


def default():
    b = Bucket()
    for f in default_filters:
        b.add_match_filter(f)
    return b

default_filters = [conflict_prefer_longer]

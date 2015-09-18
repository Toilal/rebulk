#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bucket class and factories
"""

from .filters import conflict_prefer_longer


class Bucket(object):
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
    """
    Builds a default Bucket with preconfigured filters

    :return: A new bucket
    :rtype: Bucket
    """
    bucket = Bucket()
    for filter_ in DEFAULT_FILTERS:
        bucket.add_match_filter(filter_)
    return bucket

DEFAULT_FILTERS = [conflict_prefer_longer]

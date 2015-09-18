#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point functions for Rebulk
"""
from .match import Matches


def rebulk(bucket, input_string):
    """
    Perform a bulk match with configured bucket against input_string
    :param bucket: A configured bucket
    :type bucket: rebulk.bucket.Bucket
    :param input_string: string to search into
    :type input_string: str
    :return: A custom list of matches
    :rtype: Matches
    """
    matches = Matches()
    context = {}

    for pattern in bucket.patterns:
        for match in pattern.matches(input_string):
            matches.append(match)

    for func in bucket.filters:
        matches = func(matches, context)

    return matches

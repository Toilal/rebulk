#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .match import Matches


def rebulk(bucket, input_string):
    matches = Matches()
    context = {}

    for pattern in bucket.patterns:
        for match in pattern.matches(input_string):
            matches.append(match)

    for func in bucket.filters:
        matches = func(matches, context)

    return matches

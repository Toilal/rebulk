#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processor functions
"""


def conflict_prefer_longer(matches):
    """
    Remove shorter matches if they conflicts with longer ones

    :param matches:
    :type matches: rebulk.match.Matches
    :param context:
    :type context:
    :return:
    :rtype: list[rebulk.match.Match]
    """
    to_remove_matches = set()
    for match in matches:
        conflicting_matches = set()

        for i in range(*match.span):
            conflicting_matches.update(matches.starting(i))
            conflicting_matches.update(matches.ending(i))

        if conflicting_matches:
            # keep the match only if it's the longest
            for conflicting_match in conflicting_matches:
                if len(conflicting_match) < len(match):
                    to_remove_matches.add(conflicting_match)

    for match in list(to_remove_matches):
        matches.remove(match)

    return matches


def remove_private(matches):
    """
    Removes matches from private patterns.

    :param matches:
    :type matches:
    :return:
    :rtype:
    """
    to_remove_matches = set()
    for match in matches:
        if match.pattern.private:
            to_remove_matches.add(match)

    for match in list(to_remove_matches):
        matches.remove(match)

    return matches

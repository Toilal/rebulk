#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .match import start_end_hash


def conflict_prefer_longer(matches, context=None):
    """
    Remove shorter matches if they conflicts with longer ones

    :param matches:
    :type matches:
    :param context:
    :type context:
    :return:
    :rtype: list[rebulk.match.Match]
    """
    start_hash, end_hash = start_end_hash(matches)

    to_remove_matches = set()
    for match in matches:
        conflicting_matches = set()

        for i in range(*match.span):
            conflicting_matches.update(start_hash[i])
            conflicting_matches.update(end_hash[i])

        if conflicting_matches:
            # keep the match only if it's the longuest
            for conflicting_match in conflicting_matches:
                if len(conflicting_match) < len(match):
                    to_remove_matches.add(conflicting_match)
                    start_hash[i].discard(conflicting_match)
                    end_hash[i].discard(conflicting_match)

    return [x for x in matches if x not in to_remove_matches]

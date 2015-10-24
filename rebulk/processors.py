#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Processor functions
"""
from .utils import IdentitySet

DEFAULT = '__default__'


def default_conflict_solver(match, conflicting_match):
    """
    Default conflict solver for matches, shorter matches if they conflicts with longer ones

    :param conflicting_match:
    :type conflicting_match:
    :param match:
    :type match:
    :return:
    :rtype:
    """
    if len(conflicting_match.initiator) < len(match.initiator):
        return conflicting_match
    elif len(match.initiator) < len(conflicting_match.initiator):
        return match
    return None


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
    to_remove_matches = IdentitySet()
    for match in filter(lambda match: not match.private, matches):
        conflicting_matches = matches.conflicting(match)

        if conflicting_matches:
            # keep the match only if it's the longest
            for conflicting_match in filter(lambda match: not match.private, conflicting_matches):
                reverse = False
                conflict_solvers = [(default_conflict_solver, False)]

                if match.conflict_solver:
                    conflict_solvers.append((match.conflict_solver, False))
                if conflicting_match.conflict_solver:
                    conflict_solvers.append((conflicting_match.conflict_solver, True))

                for conflict_solver, reverse in reversed(conflict_solvers):
                    if reverse:
                        to_remove = conflict_solver(conflicting_match, match)
                    else:
                        to_remove = conflict_solver(match, conflicting_match)
                    if to_remove == DEFAULT:
                        continue
                    if to_remove and to_remove not in to_remove_matches:
                        to_remove_matches.add(to_remove)
                    break

    for match in to_remove_matches:
        matches.remove(match)

    return matches


def remove_private(matches):
    """
    Removes private matches.

    :param matches:
    :type matches:
    :return:
    :rtype:
    """
    for match in list(matches):
        if match.private:
            matches.remove(match)

    return matches

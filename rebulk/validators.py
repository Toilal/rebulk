#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validator functions to use in patterns.

All those function have last argument as match, so it's possible to use functools.partial to bind previous arguments.
"""


def chars_before(chars, match):
    """
    Validate the match if left character is in a given sequence.

    :param chars:
    :type chars:
    :param match:
    :type match:
    :return:
    :rtype:
    """
    if match.start <= 0:
        return True
    return match.input_string[match.start - 1] in chars


def chars_after(chars, match):
    """
    Validate the match if left character is in a given sequence.

    :param chars:
    :type chars:
    :param match:
    :type match:
    :return:
    :rtype:
    """
    if match.end >= len(match.input_string):
        return True
    return match.input_string[match.end] in chars


def chars_surround(chars, match):
    """
    Validate the match if surrounding characters are in a given sequence.

    :param chars:
    :type chars:
    :param match:
    :type match:
    :return:
    :rtype:
    """
    return chars_before(chars, match) and chars_after(chars, match)


def chain(validators, match):
    """
    Creates a validator chain from several validator functions.

    :param validators:
    :type validators:
    :return:
    :rtype:
    """
    for validator in validators:
        if not validator(match):
            return False
    return True

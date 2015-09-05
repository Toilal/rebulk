#!/usr/bin/env python
# -*- coding: utf-8 -*-

def find_all(s, sub, start=None, end=None):
    """
    Return all indices in string s where substring sub is
    found, such that sub is contained in the slice s[start:end].

    >>> list(find_all('The quick brown fox jumps over the lazy dog', 'fox'))
    [16]

    >>> list(find_all('The quick brown fox jumps over the lazy dog', 'mountain'))
    []

    >>> list(find_all('The quick brown fox jumps over the lazy dog', 'The'))
    [0]

    >>> list(find_all(
    ... 'Carved symbols in a mountain hollow on the bank of an inlet irritated an eccentric person',
    ... 'an'))
    [44, 51, 70]

    >>> list(find_all(
    ... 'Carved symbols in a mountain hollow on the bank of an inlet irritated an eccentric person',
    ... 'an',
    ... 50,
    ... 60))
    [51]

    :param s: the input string
    :type s: str
    :param sub: the substring
    :type sub: str
    :return: all indices in the input string
    :rtype: __generator[str]
    """
    while True:
        start = s.find(sub, start, end)
        if start == -1:
            return
        yield start
        start += len(sub)

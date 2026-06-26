#!/usr/bin/env python
"""
Formatter functions to use in patterns.

All those function have last argument as match.value (str).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


def formatters(*chained_formatters: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Chain formatter functions.
    :param chained_formatters:
    :type chained_formatters:
    :return:
    :rtype:
    """

    def formatters_chain(input_string: Any) -> Any:  # pylint:disable=missing-docstring
        for chained_formatter in chained_formatters:
            input_string = chained_formatter(input_string)
        return input_string

    return formatters_chain


def default_formatter(input_string: Any) -> Any:
    """
    Default formatter
    :param input_string:
    :return:
    """
    return input_string

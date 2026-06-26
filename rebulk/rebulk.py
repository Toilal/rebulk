#!/usr/bin/env python
"""
Entry point functions and classes for Rebulk
"""

from __future__ import annotations

from collections.abc import Callable
from logging import getLogger
from typing import TYPE_CHECKING, Any, cast

from .builder import Builder
from .match import Match, Matches
from .pattern import Pattern
from .processors import ConflictSolver, PrivateRemover
from .rules import CustomRule, Rules
from .utils import extend_safe

if TYPE_CHECKING:
    from typing_extensions import Self

log = getLogger(__name__).log


class Rebulk(Builder):
    r"""
    Regular expression, string and function based patterns are declared in a ``Rebulk`` object. It use a fluent API to
    chain ``string``, ``regex``, and ``functional`` methods to define various patterns types.

    .. code-block:: python

        >>> from rebulk import Rebulk
        >>> bulk = Rebulk().string('brown').regex(r'qu\w+').functional(lambda s: (20, 25))

    When ``Rebulk`` object is fully configured, you can call ``matches`` method with an input string to retrieve all
    ``Match`` objects found by registered pattern.

    .. code-block:: python

        >>> bulk.matches("The quick brown fox jumps over the lazy dog")
        [<brown:(10, 15)>, <quick:(4, 9)>, <jumps:(20, 25)>]

    If multiple ``Match`` objects are found at the same position, only the longer one is kept.

    .. code-block:: python

        >>> bulk = Rebulk().string('lakers').string('la')
        >>> bulk.matches("the lakers are from la")
        [<lakers:(4, 10)>, <la:(20, 22)>]
    """

    # pylint:disable=protected-access

    def __init__(
        self,
        disabled: bool | Callable[[dict[str, Any] | None], bool] = lambda context: False,
        default_rules: bool = True,
    ) -> None:
        """
        Creates a new Rebulk object.
        :param disabled: if True, this pattern is disabled. Can also be a function(context).
        :type disabled: bool|function
        :param default_rules: use default rules
        :type default_rules:
        :return:
        :rtype:
        """
        super().__init__()
        self.disabled: Callable[[dict[str, Any] | None], bool]
        if not callable(disabled):
            self.disabled = lambda context: disabled
        else:
            self.disabled = disabled
        self._patterns: list[Pattern] = []
        self._rules = Rules()
        if default_rules:
            self.rules(ConflictSolver, PrivateRemover)
        self._rebulks: list[Rebulk] = []

    def pattern(self, *pattern: Pattern) -> Self:
        """
        Add patterns objects

        :param pattern:
        :type pattern: rebulk.pattern.Pattern
        :return: self
        :rtype: Rebulk
        """
        self._patterns.extend(pattern)
        return self

    def rules(self, *rules: CustomRule | type[CustomRule] | Any) -> Self:
        """
        Add rules as a module, class or instance.
        :param rules:
        :type rules: list[Rule]
        :return:
        """
        self._rules.load(*rules)
        return self

    def rebulk(self, *rebulks: Rebulk) -> Self:
        """
        Add a children rebulk object
        :param rebulks:
        :type rebulks: Rebulk
        :return:
        """
        self._rebulks.extend(rebulks)
        return self

    def matches(self, string: str, context: dict[str, Any] | None = None) -> Matches:
        """
        Search for all matches with current configuration against input_string
        :param string: string to search into
        :type string: str
        :param context: context to use
        :type context: dict
        :return: A custom list of matches
        :rtype: Matches
        """
        matches = Matches(input_string=string)
        if context is None:
            context = {}

        self._matches_patterns(matches, context)

        self._execute_rules(matches, context)

        return matches

    def effective_rules(self, context: dict[str, Any] | None = None) -> Rules:
        """
        Get effective rules for this rebulk object and its children.
        :param context:
        :type context:
        :return:
        :rtype:
        """
        rules = Rules()
        rules.extend(self._rules)
        for rebulk in self._rebulks:
            if not rebulk.disabled(context):
                extend_safe(rules, rebulk._rules)
        return rules

    def _execute_rules(self, matches: Matches, context: dict[str, Any]) -> None:
        """
        Execute rules for this rebulk and children.
        :param matches:
        :type matches:
        :param context:
        :type context:
        :return:
        :rtype:
        """
        if not self.disabled(context):
            rules = self.effective_rules(context)
            rules.execute_all_rules(matches, context)

    def effective_patterns(self, context: dict[str, Any] | None = None) -> list[Pattern]:
        """
        Get effective patterns for this rebulk object and its children.
        :param context:
        :type context:
        :return:
        :rtype:
        """
        patterns = list(self._patterns)
        for rebulk in self._rebulks:
            if not rebulk.disabled(context):
                extend_safe(patterns, rebulk._patterns)
        return patterns

    def _matches_patterns(self, matches: Matches, context: dict[str, Any]) -> None:
        """
        Search for all matches with current paterns agains input_string
        :param matches: matches list
        :type matches: Matches
        :param context: context to use
        :type context: dict
        :return:
        :rtype:
        """
        if not self.disabled(context):
            patterns = self.effective_patterns(context)
            for pattern in patterns:
                if not pattern.disabled(context):
                    pattern_matches = cast("list[Match]", pattern.matches(cast("str", matches.input_string), context))
                    if pattern_matches:
                        log(pattern.log_level, "Pattern has %s match(es). (%s)", len(pattern_matches), pattern)
                    else:
                        pass
                        # log(pattern.log_level, "Pattern doesn't match. (%s)" % (pattern,))
                    for match in pattern_matches:
                        if match.marker:
                            log(pattern.log_level, "Marker found. (%s)", match)
                            matches.markers.append(match)
                        else:
                            log(pattern.log_level, "Match found. (%s)", match)
                            matches.append(match)
                else:
                    log(pattern.log_level, "Pattern is disabled. (%s)", pattern)

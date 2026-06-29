#!/usr/bin/env python
"""
Base builder class for Rebulk
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any

from .loose import set_defaults
from .pattern import FunctionalPattern, RePattern, StringPattern

if TYPE_CHECKING:
    from collections.abc import Iterator

    from typing_extensions import Self

    from .chain import Chain
    from .key import Key

log = getLogger(__name__).log


def _apply_key(key: Key[Any] | None, kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Inject a typed :class:`~rebulk.key.Key`'s name and converter (its explicit
    ``formatter`` or its ``value_type``) into pattern kwargs, without overriding
    explicit values.
    """
    if key is not None:
        kwargs.setdefault("name", key.name)
        kwargs.setdefault("formatter", key.converter)
    return kwargs


@contextmanager
def overrides(kwargs: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """
    Implements override kwarg to restore initial kwarg arguments from overrides list after set_defaults calls.
    :param kwargs:
    :return:
    """
    override_keys = kwargs.pop("overrides", None)
    backup: dict[str, Any] = {}
    if override_keys:
        for override_key in override_keys:
            backup[override_key] = kwargs[override_key]

    yield backup

    kwargs.update(backup)


class Builder(metaclass=ABCMeta):
    """
    Base builder class for patterns
    """

    def __init__(self) -> None:
        self._defaults: dict[str, Any] = {}
        self._regex_defaults: dict[str, Any] = {}
        self._string_defaults: dict[str, Any] = {}
        self._functional_defaults: dict[str, Any] = {}
        self._chain_defaults: dict[str, Any] = {}

    def reset(self) -> None:
        """
        Reset all defaults.

        :return:
        """
        self.__init__()  # type: ignore[misc]

    def defaults(self, **kwargs: Any) -> Self:
        """
        Define default keyword arguments for all patterns
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        set_defaults(kwargs, self._defaults, override=True)
        return self

    def regex_defaults(self, **kwargs: Any) -> Self:
        """
        Define default keyword arguments for functional patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        set_defaults(kwargs, self._regex_defaults, override=True)
        return self

    def string_defaults(self, **kwargs: Any) -> Self:
        """
        Define default keyword arguments for string patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        set_defaults(kwargs, self._string_defaults, override=True)
        return self

    def functional_defaults(self, **kwargs: Any) -> Self:
        """
        Define default keyword arguments for functional patterns.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        set_defaults(kwargs, self._functional_defaults, override=True)
        return self

    def chain_defaults(self, **kwargs: Any) -> Self:
        """
        Define default keyword arguments for patterns chain.
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        set_defaults(kwargs, self._chain_defaults, override=True)
        return self

    def build_re(self, *pattern: Any, **kwargs: Any) -> RePattern:
        """
        Builds a new regular expression pattern

        :param pattern:
        :type pattern:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        with overrides(kwargs):
            set_defaults(self._regex_defaults, kwargs)
            set_defaults(self._defaults, kwargs)

        return RePattern(*pattern, **kwargs)

    def build_string(self, *pattern: Any, **kwargs: Any) -> StringPattern:
        """
        Builds a new string pattern

        :param pattern:
        :type pattern:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        with overrides(kwargs):
            set_defaults(self._string_defaults, kwargs)
            set_defaults(self._defaults, kwargs)

        return StringPattern(*pattern, **kwargs)

    def build_functional(self, *pattern: Any, **kwargs: Any) -> FunctionalPattern:
        """
        Builds a new functional pattern

        :param pattern:
        :type pattern:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        with overrides(kwargs):
            set_defaults(self._functional_defaults, kwargs)
            set_defaults(self._defaults, kwargs)

        return FunctionalPattern(*pattern, **kwargs)

    def build_chain(self, **kwargs: Any) -> Chain:
        """
        Builds a new patterns chain

        :param pattern:
        :type pattern:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        from .chain import Chain

        with overrides(kwargs):
            set_defaults(self._chain_defaults, kwargs)
            set_defaults(self._defaults, kwargs)

        chain = Chain(self, **kwargs)
        chain._defaults = deepcopy(self._defaults)
        chain._regex_defaults = deepcopy(self._regex_defaults)
        chain._functional_defaults = deepcopy(self._functional_defaults)
        chain._string_defaults = deepcopy(self._string_defaults)
        chain._chain_defaults = deepcopy(self._chain_defaults)

        return chain

    @abstractmethod
    def pattern(self, *pattern: Any) -> Self:
        """
        Register a list of Pattern instance
        :param pattern:
        :return:
        """

    def regex(self, *pattern: Any, key: Key[Any] | None = None, **kwargs: Any) -> Self:
        """
        Add re pattern

        :param pattern:
        :type pattern:
        :param key: optional typed key wiring up the match name and value type.
        :return: self
        :rtype: Rebulk
        """
        return self.pattern(self.build_re(*pattern, **_apply_key(key, kwargs)))

    def string(self, *pattern: Any, key: Key[Any] | None = None, **kwargs: Any) -> Self:
        """
        Add string pattern

        :param pattern:
        :type pattern:
        :param key: optional typed key wiring up the match name and value type.
        :return: self
        :rtype: Rebulk
        """
        return self.pattern(self.build_string(*pattern, **_apply_key(key, kwargs)))

    def functional(self, *pattern: Any, key: Key[Any] | None = None, **kwargs: Any) -> Self:
        """
        Add functional pattern

        :param pattern:
        :type pattern:
        :param key: optional typed key wiring up the match name and value type.
        :return: self
        :rtype: Rebulk
        """
        functional = self.build_functional(*pattern, **_apply_key(key, kwargs))
        return self.pattern(functional)

    def chain(self, **kwargs: Any) -> Chain:
        """
        Add patterns chain, using configuration of this rebulk

        :param pattern:
        :type pattern:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        chain = self.build_chain(**kwargs)
        self.pattern(chain)
        return chain

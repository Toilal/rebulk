#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Abstract rule class definition and rule engine implementation
"""
from abc import ABCMeta, abstractmethod
import inspect
from itertools import groupby

import six
from .utils import is_iterable


@six.add_metaclass(ABCMeta)
class Rule(object):
    """
    Definition of a rule to apply
    """
    # pylint: disable=no-self-use, unused-argument
    priority = 0
    name = None

    def __init__(self):
        pass

    def enabled(self, context):
        """
        Disable rule.

        :param context:
        :type context:
        :return: True if rule is enabled, False if disabled
        :rtype: bool
        """
        return True

    @abstractmethod
    def when(self, matches, context):  # pragma: no cover
        """
        Condition implementation.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context:
        :return: truthy if rule should be triggered and execute then action, falsy if it should not.
        :rtype: object
        """
        pass

    @abstractmethod
    def then(self, matches, when_response, context):  # pragma: no cover
        """
        Action implementation.

        :param matches:
        :type matches: rebulk.match.Matches
        :param context:
        :type context:
        :param when_response: return object from when call.
        :type when_response: object
        :return: True if the action was runned, False if it wasn't.
        :rtype: bool
        """
        pass

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return self.name if self.name else self.__class__.__name__


class RemoveMatchRule(Rule):  # pylint: disable=abstract-method
    """
    Remove matches returned by then
    """
    def then(self, matches, when_response, context):
        if is_iterable(when_response):
            for match in when_response:
                matches.remove(match)
        else:
            matches.remove(when_response)


class AppendMatchRule(Rule):  # pylint: disable=abstract-method
    """
    Append matches returned by then
    """
    def then(self, matches, when_response, context):
        if is_iterable(when_response):
            for match in when_response:
                matches.append(match)
        else:
            matches.append(when_response)


class AppendRemoveMatchRule(Rule):  # pylint: disable=abstract-method
    """
    Append matches returned by then[0] and remove matches returned by then[1]
    """
    def then(self, matches, when_response, context):
        to_append, to_remove = when_response
        if is_iterable(to_append):
            for match in to_append:
                matches.append(match)
        else:
            matches.append(to_append)
        if is_iterable(to_remove):
            for match in to_remove:
                matches.remove(match)
        else:
            matches.append(to_remove)




class Rules(list):
    """
    list of rules ready to execute.
    """

    def __init__(self, *rules):
        super(Rules, self).__init__()
        self.load(*rules)

    def load(self, *rules):
        """
        Load rules from a Rule module, class or instance

        :param rules:
        :type rules:
        :return:
        :rtype:
        """
        for rule in rules:
            if inspect.ismodule(rule):
                self.load_module(rule)
            elif inspect.isclass(rule):
                self.load_class(rule)
            else:
                self.append(rule)

    def load_module(self, module):
        """
        Load a rules module

        :param module:
        :type module:
        :return:
        :rtype:
        """
        # pylint: disable=unused-variable
        for name, obj in inspect.getmembers(module,
                                            lambda member: hasattr(member, '__module__')
                                            and member.__module__ == module.__name__
                                            and inspect.isclass):
            self.load_class(obj)

    def load_class(self, class_):
        """
        Load a Rule class.

        :param class_:
        :type class_:
        :return:
        :rtype:
        """
        self.append(class_())

    def execute_all_rules(self, matches, context):
        """
        Execute all rules from this rules list. All when condition with same priority will be performed before
        calling then actions.

        :param matches:
        :type matches:
        :param context:
        :type context:
        :return:
        :rtype:
        """
        ret = []
        rules = sorted(self)
        for _, priority_rules in groupby(rules, lambda rule: rule.priority):
            then_futures = []
            for rule in priority_rules:
                if rule.enabled(context):
                    when_response = rule.when(matches, context)
                    if when_response:
                        then_futures.append((rule, matches, when_response, context))
            for then_future in then_futures:
                rule = then_future[0]
                args = then_future[1:]
                when_response = then_future[2]
                rule.then(*args)
                ret.append((rule, when_response))
        return ret

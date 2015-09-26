#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various utilities functions
"""
import inspect
import sys
from .utils import is_iterable

if sys.version_info < (3, 4, 0):  # pragma: no cover
    def _constructor(class_):
        """
        Retrieves constructor from given class

        :param class_:
        :type class_: class
        :return: constructor from given class
        :rtype: callable
        """
        return class_.__init__
else:  # pragma: no cover
    def _constructor(class_):
        """
        Retrieves constructor from given class

        :param class_:
        :type class_: class
        :return: constructor from given class
        :rtype: callable
        """
        return class_


def call(function, *args, **kwargs):
    """
    Call a function or constructor with given args and kwargs after removing args and kwargs that doesn't match
    function or constructor signature

    :param function: Function or constructor to call
    :type function: callable
    :param args:
    :type args:
    :param kwargs:
    :type kwargs:
    :return: sale vakye as default function call
    :rtype: object
    """
    func = constructor_args if inspect.isclass(function) else function_args
    call_args, call_kwargs = func(function, *args, **kwargs)
    return function(*call_args, **call_kwargs)


def function_args(callable_, *args, **kwargs):
    """
    Return (args, kwargs) matching the function signature

    :param callable: callable to inspect
    :type callable: callable
    :param args:
    :type args:
    :param kwargs:
    :type kwargs:
    :return: (args, kwargs) matching the function signature
    :rtype: tuple
    """
    argspec = inspect.getargspec(callable_)
    call_kwarg = {k: kwargs[k] for k in kwargs if k in argspec.args}
    call_args = args[:len(argspec.args)]
    return call_args, call_kwarg


def constructor_args(class_, *args, **kwargs):
    """
    Return (args, kwargs) matching the function signature

    :param callable: callable to inspect
    :type callable: Callable
    :param args:
    :type args:
    :param kwargs:
    :type kwargs:
    :return: (args, kwargs) matching the function signature
    :rtype: tuple
    """
    argspec = inspect.getargspec(_constructor(class_))
    call_kwarg = {k: kwargs[k] for k in kwargs if k in argspec.args}
    call_args = args[:len(argspec.args)-1]
    return call_args, call_kwarg


def ensure_list(param):
    """
    Retrieves a list from given parameter.

    :param param:
    :type param:
    :return:
    :rtype:
    """
    if not param:
        param = []
    elif not is_iterable(param):
        param = [param]
    return param


def ensure_dict(param, default_value, default_key=None):
    """
    Retrieves a dict from given parameter.

    :param param:
    :type param:
    :param default_value:
    :type default_value:
    :param default_key:
    :type default_key:
    :return:
    :rtype:
    """
    if not param:
        param = default_value
    if not isinstance(param, dict):
        return {default_key: param}
    return param


def filter_index(collection, predicate=None, index=None):
    """
    Filter collection with predicate function and index.

    If index is not found, returns None.
    :param collection:
    :type collection: collection supporting iteration and slicing
    :param predicate: function to filter the collection with
    :type predicate: function
    :param index: position of a single element to retrieve
    :type index: int
    :return: filtered list, or single element of filtered list if index is defined
    :rtype: list or object
    """
    if index is None and isinstance(predicate, int):
        index = predicate
        predicate = None
    if predicate:
        collection = collection.__class__(filter(predicate, collection))
    if index is not None:
        try:
            collection = collection[index]
        except IndexError:
            collection = None
    return collection

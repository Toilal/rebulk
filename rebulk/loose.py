#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various utilities functions
"""
import inspect
import sys

if sys.version_info < (3, 4, 0):  # pragma: no cover
    def _constructor(function):
        """
        Returns the constructor of class
        """
        return function.__init__
else:  # pragma: no cover
    def _constructor(function):
        """
        Returns the constructor of class
        """
        return function


def call(function, *args, **kwargs):
    """
    Call a function or constructor with given args and kwargs after removing args and kwargs that doesn't match
    function or constructor signature

    :param init:
    :type init:
    :return:
    :rtype:
    """
    func = constructor_args if inspect.isclass(function) else function_args
    call_args, call_kwargs = func(function, *args, **kwargs)
    return function(*call_args, **call_kwargs)

def function_args(callable_, *args, **kwargs):
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

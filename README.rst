ReBulk
=======

.. image:: http://img.shields.io/pypi/v/rebulk.svg
    :target: https://pypi.python.org/pypi/rebulk
    :alt: Latest Version

.. image:: http://img.shields.io/badge/license-MIT-blue.svg
    :target: https://pypi.python.org/pypi/rebulk
    :alt: License

.. image:: http://img.shields.io/travis/Toilal/rebulk.svg
    :target: http://travis-ci.org/Toilal/rebulk
    :alt: Build Status

.. image:: http://img.shields.io/coveralls/Toilal/rebulk.svg
    :target: https://coveralls.io/r/Toilal/rebulk?branch=master
    :alt: Coveralls

ReBulk is a python library that performs advanced searches in strings that would be hard to implement using
`re module`_ or `String methods`_ only.

Install
-------
.. code-block:: sh

    $ pip install rebulk

Usage
------
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

String Patterns
---------------
String patterns are based on `str.find`_ method to find matches, but returns all matches in the string.

.. code-block:: python

    >>> Rebulk().string('la').matches("lalalilala")
    [<la:(0, 2)>, <la:(2, 4)>, <la:(6, 8)>, <la:(8, 10)>]

You can define several patterns with a single ``string`` method call.

.. code-block:: python

    >>> Rebulk().string('Winter', 'coming').matches("Winter is coming...")
    [<Winter:(0, 6)>, <coming:(10, 16)>]

Regular Expression Patterns
---------------------------
Regular Expression patterns are based on a compiled regular expression.
`re.finditer`_ method is used to find matches.

.. code-block:: python

    >>> Rebulk().regex(r'l\w').matches("lolita")
    [<lo:(0, 2)>, <li:(2, 4)>]

You can define several patterns with a single ``regex`` method call.

.. code-block:: python

    >>> Rebulk().regex(r'Wint\wr', 'com\w{3}').matches("Winter is coming...")
    [<Winter:(0, 6)>, <coming:(10, 16)>]

All keyword arguments from `re.compile`_ are supported.

.. code-block:: python

    >>> import re  # import required for flags constant
    >>> Rebulk().regex('L[A-Z]KERS', flags=re.IGNORECASE) \
    ...         .matches("The LaKeRs are from La")
    [<LaKeRs:(4, 10)>]

    >>> Rebulk().regex('L[A-Z]', 'L[A-Z]KERS', flags=re.IGNORECASE) \
    ...         .matches("The LaKeRs are from La")
    [<La:(20, 22)>, <LaKeRs:(4, 10)>]

    >>> Rebulk().regex(('L[A-Z]', re.IGNORECASE), ('L[a-z]KeRs')) \
    ...         .matches("The LaKeRs are from La")
    [<La:(20, 22)>, <LaKeRs:(4, 10)>]

Functional Patterns
-------------------
Functional Patterns are based on the evaluation of a function.

The function should have the same parameters as ``Rebulk.matches`` method, that is the input string,
and must return both start index and end index of the ``Match`` object.

.. code-block:: python

    >>> def func(string):
    ...     index = string.find('?')
    ...     if index > -1:
    ...         return 0, index - 11
    >>> Rebulk().functional(func).matches("Why do simple ? Forget about it ...")
    [<Why:(0, 3)>]

You can define several patterns with a single ``functional`` method call.


Patterns parameters
-------------------

All patterns have options that can be given as keyword arguments.

- formatter

  Function to convert ``Match`` value given by the pattern.

  .. code-block:: python

      >>> def year_formatter(value):
      ...     return int(value)
      >>> matches = Rebulk().regex(r'\d{4}', formatter=year_formatter) \
      ...                   .matches("In year 1982 ...")
      >>> isinstance(matches[0].value, int)
      True

- label, tags, examples

  TODO

It also pass ``name`` and ``value`` keyword arguments to generated ``Match`` objects.


Match
-----

A ``Match`` object is the result created by a registered pattern.

It has a ``value`` property defined, and position indices are available through ``start``, ``end`` and ``span``
properties.

In some case, it contains children ``Match`` objects in ``children`` property, and each child ``Match`` object
reference its parent in ``parent`` property. Also, a ``name`` property can be defined for the match.

If groups are defined in a Regular Expression pattern, each group match will be converted to a
single ``Match`` object. If a group has a name defined (``(?P<name>group)``), it is set as ``name`` property in a child
``Match`` object. The whole regexp match (``re.group(0)``) will be converted to the main ``Match`` object,
and all subgroups (1, 2, ... n) will be converted to ``children`` matches of the main ``Match`` object.

.. code-block:: python

    >>> matches = Rebulk() \
    ...         .regex(r"One, (?P<one>\w+), Two, (?P<two>\w+), Three, (?P<three>\w+)") \
    ...         .matches("Zero, 0, One, 1, Two, 2, Three, 3, Four, 4")
    >>> matches
    [<One, 1, Two, 2, Three, 3:(9, 33)>]
    >>> for child in matches[0].children:
    ...     '%s = %s' % (child.name, child.value)
    'one = 1'
    'two = 2'
    'three = 3'


Matches
-------

A ``Matches`` object holds the result of ``Rebulk.matches`` method call. It's a sequence of ``Match`` objects and
it behaves like a list.

It has additional methods on it, like ``starting(index)``/``ending(index)`` that retrieves a list of ``Match`` objects
start starts/ends at a given index.

Processors
----------
Processors are functions that can be registered to ``Rebulk`` object with ``processor`` method.

All registered processors will be executed sequentially to modify the default sequence of ``Match`` returned by
patterns.

Rebulk embeds some processors in ``processors`` module.

``conflict_prefer_longer`` (enabled by default) is used to keep only longer matches when several matches shares the
same characters.

Default processors can be disabled when creating ``Rebulk`` object with ``default`` argument set to ``False``.

.. code-block:: python

    >>> bulk = Rebulk(default=False).string('la', 'lakers')
    >>> bulk.matches("the lakers are from la")
    [<la:(4, 6)>, <la:(20, 22)>, <lakers:(4, 10)>]

.. _re module: https://docs.python.org/3/library/re.html
.. _String methods: https://docs.python.org/3/library/stdtypes.html#str
.. _str.find: https://docs.python.org/3/library/stdtypes.html#str.find
.. _re.finditer: https://docs.python.org/3/library/re.html#re.finditer
.. _re.compile: https://docs.python.org/3/library/re.html#re.compile


ReBulk
======

[![Latest Version](https://img.shields.io/pypi/v/rebulk.svg)](https://pypi.python.org/pypi/rebulk)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Toilal/rebulk/blob/develop/LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/Toilal/rebulk/ci.yml?branch=develop)](https://github.com/Toilal/rebulk/actions/workflows/ci.yml)
[![Codecov](https://img.shields.io/codecov/c/github/Toilal/rebulk)](https://codecov.io/gh/Toilal/rebulk)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/relekang/python-semantic-release)

ReBulk is a python library that performs advanced searches in strings that would
be hard to implement using [re](https://docs.python.org/3/library/re.html) or
[string methods](https://docs.python.org/3/library/stdtypes.html#str) only.

It provides `Patterns`, `Match`, `Rule` and a fluent API to build a custom and
complex string matcher that stays readable and extendable.

Install
=======

```sh
$ pip install rebulk
```

Usage
=====

String, regular expression and function based patterns are declared on a
`Rebulk` object, then `matches` returns every `Match` found in the input string.

```python
>>> from rebulk import Rebulk
>>> bulk = Rebulk().string('brown').regex(r'qu\w+').functional(lambda s: (20, 25))
>>> bulk.matches("The quick brown fox jumps over the lazy dog")
[<brown:(10, 15)>, <quick:(4, 9)>, <jumps:(20, 25)>]

```

From there you can name and tag matches, validate and format their values,
compose patterns into chains, and register rules that inspect and rewrite the
match set. See the [documentation](https://toilal.github.io/rebulk/) for the
full API and advanced patterns.

Documentation
=============

Full documentation is available at
[toilal.github.io/rebulk](https://toilal.github.io/rebulk/). A preview of the
in-development `develop` branch is published at
[toilal.github.io/rebulk/dev](https://toilal.github.io/rebulk/dev/).

Support
=======

This project is hosted on [GitHub](https://github.com/Toilal/rebulk). Feel free
to open an issue if you think you have found a bug or something is missing.

License
=======

ReBulk is licensed under the [MIT license](LICENSE).

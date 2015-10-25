#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define simple search patterns in bulk to perform advanced matching on any string.
"""

from .rebulk import Rebulk
from .match import Match
from .rules import Rule, AppendMatchRule, RemoveMatchRule, AppendRemoveMatchRule
from .pattern import REGEX_AVAILABLE

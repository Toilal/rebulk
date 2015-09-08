#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Match:
    def __init__(self, pattern, start, end, name=None, parent=None, value=None):
        self.pattern = pattern
        self.start = start
        self.end = end
        self.name = name
        self.parent = parent
        self.value = value

    @property
    def span(self):
        return self.start, self.end

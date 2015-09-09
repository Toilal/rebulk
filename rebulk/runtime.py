#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Context(dict):
    pass

class Request:
    """
    A request is the runtime object created for each rebulk request.

    It contains context data related to the current request.
    """
    patterns = []
    filters = []

    context = Context()

    def __init__(self, bucket, input_string):
        self.bucket = bucket
        self.input_string = input_string

    def execute(self):
        matches = []

        for pattern in self.bucket.patterns:
            for match in pattern.matches(self.input_string):
                matches.append(match)

        for func in self.bucket.filters:
            matches = func(matches, self.context)

        return Response(matches)

class Response:
    """
    A response is the result of a request.

    It contains parsed data in an understandable format.
    """

    def __init__(self, matches):
        self.matches = matches

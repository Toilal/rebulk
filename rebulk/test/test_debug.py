#!/usr/bin/env python
# pylint: disable=pointless-statement, missing-docstring, protected-access, invalid-name, len-as-condition

from .. import debug
from ..match import Match
from ..pattern import StringPattern
from ..rebulk import Rebulk
from .default_rules_module import RuleRemove0


class TestDebug:
    # request.addfinalizer(disable_debug)

    debug.DEBUG = True
    pattern = StringPattern(1, 3, value="es")

    match = Match(1, 3, value="es")
    rule = RuleRemove0()

    input_string = "This is a debug test"
    rebulk = Rebulk().string("debug").string("is")

    matches = rebulk.matches(input_string)
    debug.DEBUG = False

    @classmethod
    def setup_class(cls) -> None:
        debug.DEBUG = True

    @classmethod
    def teardown_class(cls) -> None:
        debug.DEBUG = False

    def test_pattern(self) -> None:
        assert self.pattern.defined_at.lineno > 0  # type: ignore[union-attr]
        assert self.pattern.defined_at.name == "rebulk.test.test_debug"  # type: ignore[union-attr]
        assert self.pattern.defined_at.filename.endswith("test_debug.py")  # type: ignore[union-attr]

        assert str(self.pattern.defined_at).startswith("test_debug.py#L")
        assert repr(self.pattern).startswith("<StringPattern@test_debug.py#L")

    def test_match(self) -> None:
        assert self.match.defined_at.lineno > 0  # type: ignore[union-attr]
        assert self.match.defined_at.name == "rebulk.test.test_debug"  # type: ignore[union-attr]
        assert self.match.defined_at.filename.endswith("test_debug.py")  # type: ignore[union-attr]

        assert str(self.match.defined_at).startswith("test_debug.py#L")

    def test_rule(self) -> None:
        assert self.rule.defined_at.lineno > 0  # type: ignore[union-attr]
        assert self.rule.defined_at.name == "rebulk.test.test_debug"  # type: ignore[union-attr]
        assert self.rule.defined_at.filename.endswith("test_debug.py")  # type: ignore[union-attr]

        assert str(self.rule.defined_at).startswith("test_debug.py#L")
        assert repr(self.rule).startswith("<RuleRemove0@test_debug.py#L")

    def test_rebulk(self) -> None:
        assert self.rebulk._patterns[0].defined_at.lineno > 0  # type: ignore[union-attr]
        assert self.rebulk._patterns[0].defined_at.name == "rebulk.test.test_debug"  # type: ignore[union-attr]
        assert self.rebulk._patterns[0].defined_at.filename.endswith("test_debug.py")  # type: ignore[union-attr]

        assert str(self.rebulk._patterns[0].defined_at).startswith("test_debug.py#L")

        assert self.rebulk._patterns[1].defined_at.lineno > 0  # type: ignore[union-attr]
        assert self.rebulk._patterns[1].defined_at.name == "rebulk.test.test_debug"  # type: ignore[union-attr]
        assert self.rebulk._patterns[1].defined_at.filename.endswith("test_debug.py")  # type: ignore[union-attr]

        assert str(self.rebulk._patterns[1].defined_at).startswith("test_debug.py#L")

        assert self.matches[0].defined_at == self.rebulk._patterns[0].defined_at  # pylint: disable=no-member
        assert self.matches[1].defined_at == self.rebulk._patterns[1].defined_at  # pylint: disable=no-member

    def test_repr(self) -> None:
        str(self.matches)

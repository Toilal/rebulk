#!/usr/bin/env python
from __future__ import annotations

from typing import Any

from rebulk.test.default_rules_module import (
    RuleAppend0,
    RuleAppend1,
    RuleAppend2,
    RuleAppend3,
    RuleAppendTags0,
    RuleAppendTags1,
    RuleRemove0,
    RuleRemove1,
    RuleRemoveTags0,
    RuleRemoveTags1,
    RuleRename0,
    RuleRename1,
    RuleRename2,
    RuleRename3,
)

from ..match import Match, Matches
from ..rules import Rule, Rules
from . import rules_module as rm
from .rules_module import Rule0, Rule1, Rule1Disabled, Rule2, Rule3


def test_rule_priority() -> None:
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1, Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 0
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1(), Rule0)

    rules.execute_all_rules(matches, {})
    assert len(matches) == 1
    assert matches[0] == Match(3, 4)


def test_rules_duplicates() -> None:
    rules = Rules(Rule1, Rule1)

    assert len(rules) == 1


class ParameterizedRule(Rule):
    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value

    def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
        return True

    def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
        matches.append(Match(self.value, self.value + 1))


class DependsOnParameterizedRule(Rule):
    dependency = ParameterizedRule

    def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
        return len(matches) == 2

    def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
        matches.clear()


def test_rules_distinct_instances_of_same_class() -> None:
    first, second = ParameterizedRule(1), ParameterizedRule(3)
    rules = Rules(first, second)

    assert rules == [first, second]
    assert first != second

    matches = Matches()
    rules.execute_all_rules(matches, {})

    assert [match.span for match in matches] == [(1, 2), (3, 4)]


def test_rules_same_instance_deduplicated() -> None:
    rule = ParameterizedRule(1)

    assert len(Rules(rule, rule)) == 1


def test_rules_instance_not_equal_to_class_registered_rule() -> None:
    rules = Rules(Rule1, Rule1())

    assert len(rules) == 2


def test_rules_dependency_on_class_with_several_instances() -> None:
    rules = Rules(DependsOnParameterizedRule, ParameterizedRule(1), ParameterizedRule(3))

    matches = Matches()
    rules.execute_all_rules(matches, {})

    assert len(matches) == 0


def test_rule_disabled() -> None:
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule1Disabled(), Rule2())

    rules.execute_all_rules(matches, {})
    assert len(matches) == 2
    assert matches[0] == Match(1, 2)
    assert matches[1] == Match(3, 4)


def test_rule_when() -> None:
    matches = Matches([Match(1, 2)])

    rules = Rules(Rule3())

    rules.execute_all_rules(matches, {"when": False})
    assert len(matches) == 1
    assert matches[0] == Match(1, 2)

    matches = Matches([Match(1, 2)])

    rules.execute_all_rules(matches, {"when": True})
    assert len(matches) == 2
    assert matches[0] == Match(1, 2)
    assert matches[1] == Match(3, 4)


class TestDefaultRules:
    def test_remove(self) -> None:
        rules = Rules(RuleRemove0)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 0

        rules = Rules(RuleRemove1)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 0

    def test_append(self) -> None:
        rules = Rules(RuleAppend0)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 2

        rules = Rules(RuleAppend1)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 2

        rules = Rules(RuleAppend2)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 2
        assert len(matches.named("renamed")) == 1

        rules = Rules(RuleAppend3)

        matches = Matches([Match(1, 2)])
        rules.execute_all_rules(matches, {})

        assert len(matches) == 2
        assert len(matches.named("renamed")) == 1

    def test_rename(self) -> None:
        rules = Rules(RuleRename0)

        matches = Matches([Match(1, 2, name="original")])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("original")) == 1
        assert len(matches.named("renamed")) == 0

        rules = Rules(RuleRename1)

        matches = Matches([Match(5, 10, name="original")])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("original")) == 0
        assert len(matches.named("renamed")) == 1

        rules = Rules(RuleRename2)

        matches = Matches([Match(5, 10, name="original")])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("original")) == 0
        assert len(matches.named("renamed")) == 1

        rules = Rules(RuleRename3)

        matches = Matches([Match(5, 10, name="original")])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("original")) == 0
        assert len(matches.named("renamed")) == 1

    def test_append_tags(self) -> None:
        rules = Rules(RuleAppendTags0)

        matches = Matches([Match(1, 2, name="tags", tags=["other"])])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("tags")) == 1
        assert matches.named("tags")[0].tags == ["other", "new-tag"]

        rules = Rules(RuleAppendTags1)

        matches = Matches([Match(1, 2, name="tags", tags=["other"])])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("tags")) == 1
        assert matches.named("tags")[0].tags == ["other", "new-tag"]

    def test_remove_tags(self) -> None:
        rules = Rules(RuleRemoveTags0)

        matches = Matches([Match(1, 2, name="tags", tags=["other", "new-tag"])])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("tags")) == 1
        assert matches.named("tags")[0].tags == ["other"]

        rules = Rules(RuleRemoveTags1)

        matches = Matches([Match(1, 2, name="tags", tags=["other", "new-tag"])])
        rules.execute_all_rules(matches, {})

        assert len(matches.named("tags")) == 1
        assert matches.named("tags")[0].tags == ["other"]


def test_rule_module() -> None:
    rules = Rules(rm)

    matches = Matches([Match(1, 2)])
    rules.execute_all_rules(matches, {})

    assert len(matches) == 1


def test_rule_repr() -> None:
    assert str(Rule0()) == "<Rule0>"
    assert str(Rule1()) == "<Rule1>"
    assert str(Rule2()) == "<Rule2>"
    assert str(Rule1Disabled()) == "<Disabled Rule1>"


class DependsOnUnregisteredRule1Instance(Rule):
    dependency = Rule1()

    def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
        return False


def test_rules_dependency_on_unregistered_instance_resolves_to_class() -> None:
    rules = Rules(Rule1, DependsOnUnregisteredRule1Instance)

    rules.execute_all_rules(Matches(), {})

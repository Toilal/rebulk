#!/usr/bin/env python
from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Any

from ..processors import ConflictSolver, PrivateRemover
from ..rebulk import Rebulk
from ..rules import RemoveMatch, Rule
from . import rebulk_rules_module as rm

if TYPE_CHECKING:
    from ..match import Matches


def test_rebulk_simple() -> None:
    rebulk = Rebulk()

    rebulk.string("quick")
    rebulk.regex("f.x")

    def func(input_string: str) -> tuple[int, int] | None:
        i = input_string.find("over")
        if i > -1:
            return i, i + len("over")
        return None

    rebulk.functional(func)

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string)
    assert len(matches) == 3

    assert matches[0].value == "quick"
    assert matches[1].value == "fox"
    assert matches[2].value == "over"


def test_rebulk_composition() -> None:
    rebulk = Rebulk()

    rebulk.string("quick")
    rebulk.rebulk(Rebulk().regex("f.x"))

    rebulk.rebulk(Rebulk(disabled=lambda context: True).functional(lambda string: None))

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string)
    assert len(matches) == 2

    assert matches[0].value == "quick"
    assert matches[1].value == "fox"


def test_rebulk_context() -> None:
    rebulk = Rebulk()

    context = {"nostring": True, "word": "lazy"}

    rebulk.string("quick", disabled=lambda context: context.get("nostring", False))
    rebulk.regex("f.x", disabled=lambda context: context.get("noregex", False))

    def func(input_string: str, context: dict[str, Any]) -> tuple[int, int] | None:
        word = context.get("word", "over")
        i = input_string.find(word)
        if i > -1:
            return i, i + len(word)
        return None

    rebulk.functional(func)

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string, context)
    assert len(matches) == 2

    assert matches[0].value == "fox"
    assert matches[1].value == "lazy"


def test_rebulk_prefer_longer() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = Rebulk().string("quick").string("own").regex("br.{2}n").matches(input_string)

    assert len(matches) == 2

    assert matches[0].value == "quick"
    assert matches[1].value == "brown"


def test_rebulk_defaults() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    def func(input_string: str) -> tuple[int, int] | None:
        i = input_string.find("fox")
        if i > -1:
            return i, i + len("fox")
        return None

    matches = (
        Rebulk()
        .string_defaults(name="string", tags=["a", "b"])
        .regex_defaults(name="regex")
        .functional_defaults(name="functional")
        .string("quick", tags=["c"])
        .functional(func)
        .regex("br.{2}n")
        .matches(input_string)
    )
    assert matches[0].name == "string"
    assert matches[0].tags == ["a", "b", "c"]
    assert matches[1].name == "functional"
    assert matches[2].name == "regex"

    matches = (
        Rebulk()
        .defaults(name="default", tags=["0"])
        .string_defaults(name="string", tags=["a", "b"])
        .functional_defaults(name="functional", tags=["1"])
        .string("quick", tags=["c"])
        .functional(func)
        .regex("br.{2}n")
        .matches(input_string)
    )
    assert matches[0].name == "string"
    assert matches[0].tags == ["0", "a", "b", "c"]
    assert matches[1].name == "functional"
    assert matches[1].tags == ["0", "1"]
    assert matches[2].name == "default"
    assert matches[2].tags == ["0"]


def test_rebulk_defaults_overrides() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    def func(input_string: str) -> tuple[int, int] | None:
        i = input_string.find("fox")
        if i > -1:
            return i, i + len("fox")
        return None

    matches = (
        Rebulk()
        .string_defaults(name="string", tags=["a", "b"])
        .regex_defaults(name="regex", tags=["d"])
        .functional_defaults(name="functional")
        .string("quick", tags=["c"], overrides=["tags"])
        .functional(func)
        .regex("br.{2}n")
        .matches(input_string)
    )
    assert matches[0].name == "string"
    assert matches[0].tags == ["c"]
    assert matches[1].name == "functional"
    assert matches[2].name == "regex"
    assert matches[2].tags == ["d"]

    matches = (
        Rebulk()
        .defaults(name="default", tags=["0"])
        .string_defaults(name="string", tags=["a", "b"])
        .functional_defaults(name="functional", tags=["1"])
        .string("quick", tags=["c"])
        .functional(func)
        .regex("br.{2}n")
        .matches(input_string)
    )
    assert matches[0].name == "string"
    assert matches[0].tags == ["0", "a", "b", "c"]
    assert matches[1].name == "functional"
    assert matches[1].tags == ["0", "1"]
    assert matches[2].name == "default"
    assert matches[2].tags == ["0"]


def test_rebulk_rebulk() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    base = Rebulk().string("quick")
    child = Rebulk().string("own").regex("br.{2}n")

    matches = base.rebulk(child).matches(input_string)

    assert len(matches) == 2

    assert matches[0].value == "quick"
    assert matches[1].value == "brown"


def test_rebulk_no_default() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = Rebulk(default_rules=False).string("quick").string("own").regex("br.{2}n").matches(input_string)

    assert len(matches) == 3

    assert matches[0].value == "quick"
    assert matches[1].value == "own"
    assert matches[2].value == "brown"


def test_rebulk_empty_match() -> None:
    input_string = "The quick brown fox jumps over the lazy dog"

    matches = (
        Rebulk(default_rules=False)
        .string("quick")
        .string("own")
        .regex("br(.*?)own", children=True)
        .matches(input_string)
    )

    assert len(matches) == 2

    assert matches[0].value == "quick"
    assert matches[1].value == "own"


def test_rebulk_tags_names() -> None:
    rebulk = Rebulk()

    rebulk.string("quick", name="str", tags=["first", "other"])
    rebulk.regex("f.x", tags="other")

    def func(input_string: str) -> tuple[int, int, dict[str, Any]] | None:
        i = input_string.find("over")
        if i > -1:
            return i, i + len("over"), {"tags": ["custom"]}
        return None

    rebulk.functional(func, name="fn")

    def func2(input_string: str) -> dict[str, Any] | None:
        i = input_string.find("lazy")
        if i > -1:
            return {"start": i, "end": i + len("lazy"), "tags": ["custom"]}
        return None

    rebulk.functional(func2, name="fn")

    input_string = "The quick brown fox jumps over the lazy dog"

    matches = rebulk.matches(input_string)
    assert len(matches) == 4

    assert len(matches.named("str")) == 1
    assert len(matches.named("fn")) == 2
    assert len(matches.named("false")) == 0
    assert len(matches.tagged("false")) == 0
    assert len(matches.tagged("first")) == 1
    assert len(matches.tagged("other")) == 2
    assert len(matches.tagged("custom")) == 2


def test_rebulk_rules_1() -> None:
    rebulk = Rebulk()

    rebulk.regex(r"\d{4}", name="year")
    rebulk.rules(rm.RemoveAllButLastYear)

    matches = rebulk.matches("1984 keep only last 1968 entry 1982 case")
    assert len(matches) == 1
    assert matches[0].value == "1982"


def test_rebulk_rules_2() -> None:
    rebulk = Rebulk()

    rebulk.regex(r"\d{4}", name="year")
    rebulk.string(r"year", name="yearPrefix", private=True)
    rebulk.string(r"keep", name="yearSuffix", private=True)
    rebulk.rules(rm.PrefixedSuffixedYear)

    matches = rebulk.matches("Keep suffix 1984 keep prefixed year 1968 and remove the rest 1982")
    assert len(matches) == 2
    assert matches[0].value == "1984"
    assert matches[1].value == "1968"


def test_rebulk_rules_3() -> None:
    rebulk = Rebulk()

    rebulk.regex(r"\d{4}", name="year")
    rebulk.string(r"year", name="yearPrefix", private=True)
    rebulk.string(r"keep", name="yearSuffix", private=True)
    rebulk.rules(rm.PrefixedSuffixedYearNoLambda)

    matches = rebulk.matches("Keep suffix 1984 keep prefixed year 1968 and remove the rest 1982")
    assert len(matches) == 2
    assert matches[0].value == "1984"
    assert matches[1].value == "1968"


def test_rebulk_rules_4() -> None:
    class FirstOnlyRule(Rule):
        def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
            grabbed = matches.named("grabbed", 0)
            if grabbed and matches.previous(grabbed):
                return grabbed
            return None

        def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
            matches.remove(when_response)

    rebulk = Rebulk()

    rebulk.regex("This match (.*?)grabbed", name="grabbed")
    rebulk.regex("if it's (.*?)first match", private=True)

    rebulk.rules(FirstOnlyRule)

    matches = rebulk.matches("This match is grabbed only if it's the first match")
    assert len(matches) == 1
    assert matches[0].value == "This match is grabbed"

    matches = rebulk.matches("if it's NOT the first match, This match is NOT grabbed")
    assert len(matches) == 0


class TestMarkers:
    def test_one_marker(self) -> None:
        class MarkerRule(Rule):
            def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
                word_match = matches.named("word", 0)
                if word_match is None:
                    return None
                marker = matches.markers.at_match(word_match, lambda marker: marker.name == "mark1", 0)
                if not marker:
                    return word_match
                return None

            def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
                matches.remove(when_response)

        rebulk = (
            Rebulk()
            .regex(r"\(.*?\)", marker=True, name="mark1")
            .regex(r"\[.*?\]", marker=True, name="mark2")
            .string("word", name="word")
            .rules(MarkerRule)
        )

        matches = rebulk.matches("grab (word) only if it's in parenthesis")

        assert len(matches) == 1
        assert matches[0].value == "word"

        matches = rebulk.matches("don't grab [word] if it's in braket")
        assert len(matches) == 0

        matches = rebulk.matches("don't grab word at all")
        assert len(matches) == 0

    def test_multiple_marker(self) -> None:
        class MarkerRule(Rule):
            def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
                word_match = matches.named("word", 0)
                if word_match is None:
                    return None
                marker = matches.markers.at_match(word_match, lambda marker: marker.name in ["mark1", "mark2"])
                if len(marker) < 2:
                    return word_match
                return None

            def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
                matches.remove(when_response)

        rebulk = (
            Rebulk()
            .regex(r"\(.*?\)", marker=True, name="mark1")
            .regex(r"\[.*?\]", marker=True, name="mark2")
            .regex("w.*?d", name="word")
            .rules(MarkerRule)
        )

        matches = rebulk.matches("[grab (word) only] if it's in parenthesis and brakets")

        assert len(matches) == 1
        assert matches[0].value == "word"

        matches = rebulk.matches("[don't grab](word)[if brakets are outside]")
        assert len(matches) == 0

        matches = rebulk.matches("(grab w[or)d even] if it's partially in parenthesis and brakets")
        assert len(matches) == 1
        assert matches[0].value == "w[or)d"

    def test_at_index_marker(self) -> None:
        class MarkerRule(Rule):
            def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
                word_match = matches.named("word", 0)
                if word_match is None:
                    return None
                marker = matches.markers.at_index(word_match.start, lambda marker: marker.name == "mark1", 0)
                if not marker:
                    return word_match
                return None

            def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
                matches.remove(when_response)

        rebulk = Rebulk().regex(r"\(.*?\)", marker=True, name="mark1").regex("w.*?d", name="word").rules(MarkerRule)

        matches = rebulk.matches("gr(ab wo)rd only if starting of match is inside parenthesis")

        assert len(matches) == 1
        assert matches[0].value == "wo)rd"

        matches = rebulk.matches("don't grab wo(rd if starting of match is not inside parenthesis")

        assert len(matches) == 0

    def test_remove_marker(self) -> None:
        class MarkerRule(Rule):
            def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
                marker = matches.markers.named("mark1", 0)
                if marker:
                    return marker
                return None

            def then(self, matches: Matches, when_response: Any, context: dict[str, Any] | None) -> Any:
                matches.markers.remove(when_response)

        rebulk = Rebulk().regex(r"\(.*?\)", marker=True, name="mark1").regex("w.*?d", name="word").rules(MarkerRule)

        matches = rebulk.matches("grab word event (if it's not) inside parenthesis")

        assert len(matches) == 1
        assert matches[0].value == "word"

        assert not matches.markers


class TestUnicode:
    def test_rebulk_simple(self) -> None:
        input_string = "敏捷的棕色狐狸跳過懶狗"

        rebulk = Rebulk()

        rebulk.string("敏")
        rebulk.regex("捷")

        def func(input_string: str) -> tuple[int, int] | None:
            i = input_string.find("的")
            if i > -1:
                return i, i + len("的")
            return None

        rebulk.functional(func)

        matches = rebulk.matches(input_string)
        assert len(matches) == 3

        assert matches[0].value == "敏"
        assert matches[1].value == "捷"
        assert matches[2].value == "的"


class TestImmutable:
    def test_starting(self) -> None:
        input_string = "The quick brown fox jumps over the lazy dog"
        matches = Rebulk().string("quick").string("over").string("fox").matches(input_string)

        for i in range(len(input_string)):
            starting = matches.starting(i)
            for match in list(starting):
                starting.remove(match)

        assert len(matches) == 3

    def test_ending(self) -> None:
        input_string = "The quick brown fox jumps over the lazy dog"
        matches = Rebulk().string("quick").string("over").string("fox").matches(input_string)

        for i in range(len(input_string)):
            starting = matches.ending(i)
            for match in list(starting):
                starting.remove(match)

        assert len(matches) == 3

    def test_named(self) -> None:
        input_string = "The quick brown fox jumps over the lazy dog"
        matches = Rebulk().defaults(name="test").string("quick").string("over").string("fox").matches(input_string)

        named = matches.named("test")
        for match in list(named):
            named.remove(match)

        assert len(named) == 0
        assert len(matches) == 3


class RemoveNamedRule(Rule):
    consequence = RemoveMatch

    def __init__(self, match_name: str) -> None:
        super().__init__()
        self.match_name = match_name

    def when(self, matches: Matches, context: dict[str, Any] | None) -> Any:
        return matches.named(self.match_name)


def _quick_fox_rebulk() -> Rebulk:
    return Rebulk().string("quick", name="quick").string("fox", name="fox")


def test_rebulk_rules_distinct_instances_registered_directly() -> None:
    rebulk = _quick_fox_rebulk().rules(RemoveNamedRule("quick"), RemoveNamedRule("fox"))

    assert len(rebulk.matches("The quick brown fox")) == 0


def test_rebulk_rules_distinct_instances_registered_in_child() -> None:
    child = _quick_fox_rebulk().rules(RemoveNamedRule("quick"), RemoveNamedRule("fox"))
    rebulk = Rebulk().rebulk(child)

    assert [rule.match_name for rule in rebulk.effective_rules() if isinstance(rule, RemoveNamedRule)] == [
        "quick",
        "fox",
    ]
    assert len(rebulk.matches("The quick brown fox")) == 0


def test_rebulk_rules_class_registered_in_several_children_kept_once() -> None:
    rebulk = Rebulk().rebulk(Rebulk().rules(rm.RemoveAllButLastYear), Rebulk().rules(rm.RemoveAllButLastYear))

    effective_classes = [type(rule) for rule in rebulk.effective_rules()]

    assert effective_classes.count(rm.RemoveAllButLastYear) == 1
    assert effective_classes.count(ConflictSolver) == 1
    assert effective_classes.count(PrivateRemover) == 1


def test_rebulk_rules_same_instance_in_several_children_kept_once() -> None:
    rule = RemoveNamedRule("quick")
    rebulk = Rebulk().rebulk(Rebulk().rules(rule), Rebulk().rules(rule))

    assert [r for r in rebulk.effective_rules() if isinstance(r, RemoveNamedRule)] == [rule]


def _nested(*rebulks: Rebulk) -> Rebulk:
    """Nest the given rebulks, each one being the child of the previous one."""
    for parent, child in itertools.pairwise(rebulks):
        parent.rebulk(child)
    return rebulks[0]


def test_rebulk_nested_patterns_at_any_depth() -> None:
    rebulk = _nested(Rebulk(), Rebulk(), Rebulk().string("quick", name="quick"))

    assert [match.value for match in rebulk.matches("The quick brown fox")] == ["quick"]


def test_rebulk_nested_rules_at_any_depth() -> None:
    grandchild = Rebulk().rules(RemoveNamedRule("quick"))
    rebulk = _nested(Rebulk().string("quick", name="quick"), Rebulk(), grandchild)

    assert len(rebulk.matches("The quick brown fox")) == 0


def test_rebulk_nested_default_rules_kept_once() -> None:
    rebulk = _nested(Rebulk(), Rebulk(), Rebulk())

    effective_classes = [type(rule) for rule in rebulk.effective_rules()]

    assert effective_classes == [ConflictSolver, PrivateRemover]


def test_rebulk_nested_depth_first_registration_order() -> None:
    first = Rebulk().string("a").rebulk(Rebulk().string("b"))
    rebulk = Rebulk().string("root").rebulk(first, Rebulk().string("c"))

    assert [pattern.patterns[0] for pattern in rebulk.effective_patterns()] == ["root", "a", "b", "c"]


def test_rebulk_nested_disabled_rebulk_excludes_subtree() -> None:
    disabled = Rebulk(disabled=lambda context: bool(context and context.get("off"))).rebulk(
        Rebulk().string("quick", name="quick")
    )
    rebulk = Rebulk().rebulk(disabled)

    assert len(rebulk.matches("The quick brown fox", {"off": True})) == 0
    assert len(rebulk.matches("The quick brown fox", {"off": False})) == 1


def test_rebulk_nested_shared_and_cyclic_rebulks_visited_once() -> None:
    shared = Rebulk().string("quick", name="quick")
    first, second = Rebulk().rebulk(shared), Rebulk().rebulk(shared)
    rebulk = Rebulk().rebulk(first, second)
    shared.rebulk(rebulk)

    assert len(rebulk.effective_patterns()) == 1
    assert len(rebulk.matches("The quick brown fox")) == 1

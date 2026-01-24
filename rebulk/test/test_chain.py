#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=pointless-statement, missing-docstring, no-member, len-as-condition, cyclic-import
import re
from functools import partial

from rebulk.pattern import FunctionalPattern, StringPattern, RePattern
from ..rebulk import Rebulk
from ..validators import chars_surround
from ..chain import Chain
from ..match import Match


def test_chain_close():
    rebulk = Rebulk()
    ret = rebulk.chain().close()

    assert ret == rebulk
    assert len(rebulk.effective_patterns()) == 1


def test_build_chain():
    rebulk = Rebulk()

    def digit(input_string):
        i = input_string.find("1849")
        if i > -1:
            return i, i + len("1849")

    ret = rebulk.chain() \
        .functional(digit) \
        .string("test").repeater(2) \
        .string("x").repeater('{1,3}') \
        .string("optional").repeater('?') \
        .regex("f?x").repeater('+') \
        .close()

    assert ret == rebulk
    assert len(rebulk.effective_patterns()) == 1

    chain = rebulk.effective_patterns()[0]

    assert len(chain.parts) == 5

    assert isinstance(chain.parts[0].pattern, FunctionalPattern)
    assert chain.parts[0].repeater_start == 1
    assert chain.parts[0].repeater_end == 1

    assert isinstance(chain.parts[1].pattern, StringPattern)
    assert chain.parts[1].repeater_start == 2
    assert chain.parts[1].repeater_end == 2

    assert isinstance(chain.parts[2].pattern, StringPattern)
    assert chain.parts[2].repeater_start == 1
    assert chain.parts[2].repeater_end == 3

    assert isinstance(chain.parts[3].pattern, StringPattern)
    assert chain.parts[3].repeater_start == 0
    assert chain.parts[3].repeater_end == 1

    assert isinstance(chain.parts[4].pattern, RePattern)
    assert chain.parts[4].repeater_start == 1
    assert chain.parts[4].repeater_end is None


def test_chain_defaults():
    rebulk = Rebulk()
    rebulk.defaults(validator=lambda x: x.value.startswith('t'), ignore_names=['testIgnore'], children=True)

    rebulk.chain() \
        .regex("(?P<test>test)") \
        .regex(" ").repeater("*") \
        .regex("(?P<best>best)") \
        .regex(" ").repeater("*") \
        .regex("(?P<testIgnore>testIgnore)")
    matches = rebulk.matches("test best testIgnore")

    assert len(matches) == 1
    assert matches[0].name == "test"


def test_chain_with_validators():
    def chain_validator(match):
        return match.value.startswith('t') and match.value.endswith('t')

    def default_validator(match):
        return match.value.startswith('t') and match.value.endswith('g')

    def custom_validator(match):
        return match.value.startswith('b') and match.value.endswith('t')

    rebulk = Rebulk()
    rebulk.defaults(children=True, validator=default_validator)

    rebulk.chain(validate_all=True, validator={'__parent__': chain_validator}) \
        .regex("(?P<test>testing)", validator=default_validator).repeater("+") \
        .regex(" ").repeater("+") \
        .regex("(?P<best>best)", validator=custom_validator).repeater("+")
    matches = rebulk.matches("some testing best end")

    assert len(matches) == 2
    assert matches[0].name == "test"
    assert matches[1].name == "best"


def test_matches_docs():
    rebulk = Rebulk().regex_defaults(flags=re.IGNORECASE) \
        .defaults(children=True, formatter={'episode': int, 'version': int}) \
        .chain() \
        .regex(r'e(?P<episode>\d{1,4})').repeater(1) \
        .regex(r'v(?P<version>\d+)').repeater('?') \
        .regex(r'[ex-](?P<episode>\d{1,4})').repeater('*') \
        .close()  # .repeater(1) could be omitted as it's the default behavior

    result = rebulk.matches("This is E14v2-15-16-17").to_dict()  # converts matches to dict

    assert 'episode' in result
    assert result['episode'] == [14, 15, 16, 17]
    assert 'version' in result
    assert result['version'] == 2


def test_matches():
    rebulk = Rebulk()

    def digit(input_string):
        i = input_string.find("1849")
        if i > -1:
            return i, i + len("1849")

    input_string = "1849testtestxxfixfux_foxabc1849testtestxoptionalfoxabc"

    chain = rebulk.chain() \
        .functional(digit) \
        .string("test").hidden().repeater(2) \
        .string("x").hidden().repeater('{1,3}') \
        .string("optional").hidden().repeater('?') \
        .regex("f.?x", name='result').repeater('+') \
        .close()

    matches = chain.matches(input_string)

    assert len(matches) == 2
    children = matches[0].children

    assert children[0].value == '1849'
    assert children[1].value == 'fix'
    assert children[2].value == 'fux'

    children = matches[1].children
    assert children[0].value == '1849'
    assert children[1].value == 'fox'

    input_string = "_1850testtestxoptionalfoxabc"
    matches = chain.matches(input_string)

    assert len(matches) == 0

    input_string = "_1849testtesttesttestxoptionalfoxabc"
    matches = chain.matches(input_string)

    assert len(matches) == 0

    input_string = "_1849testtestxxxxoptionalfoxabc"
    matches = chain.matches(input_string)

    assert len(matches) == 0

    input_string = "_1849testtestoptionalfoxabc"
    matches = chain.matches(input_string)

    assert len(matches) == 0

    input_string = "_1849testtestxoptionalabc"
    matches = chain.matches(input_string)

    assert len(matches) == 0

    input_string = "_1849testtestxoptionalfaxabc"
    matches = chain.matches(input_string)

    assert len(matches) == 1
    children = matches[0].children

    assert children[0].value == '1849'
    assert children[1].value == 'fax'


def test_matches_2():
    rebulk = Rebulk() \
        .regex_defaults(flags=re.IGNORECASE) \
        .defaults(children=True, formatter={'episode': int, 'version': int}) \
        .chain() \
        .regex(r'e(?P<episode>\d{1,4})') \
        .regex(r'v(?P<version>\d+)').repeater('?') \
        .regex(r'[ex-](?P<episode>\d{1,4})').repeater('*') \
        .close()

    matches = rebulk.matches("This is E14v2-15E16x17")
    assert len(matches) == 5

    assert matches[0].name == 'episode'
    assert matches[0].value == 14

    assert matches[1].name == 'version'
    assert matches[1].value == 2

    assert matches[2].name == 'episode'
    assert matches[2].value == 15

    assert matches[3].name == 'episode'
    assert matches[3].value == 16

    assert matches[4].name == 'episode'
    assert matches[4].value == 17


def test_matches_3():
    alt_dash = (r'@', r'[\W_]')  # abbreviation

    match_names = ['season', 'episode']
    other_names = ['screen_size', 'video_codec', 'audio_codec', 'audio_channels', 'container', 'date']

    rebulk = Rebulk()
    rebulk.defaults(formatter={'season': int, 'episode': int},
                    tags=['SxxExx'],
                    abbreviations=[alt_dash],
                    private_names=['episodeSeparator', 'seasonSeparator'],
                    children=True,
                    private_parent=True,
                    conflict_solver=lambda match, other: match
                    if match.name in match_names and other.name in other_names
                    else '__default__')

    rebulk.chain() \
        .defaults(children=True, private_parent=True) \
        .regex(r'(?P<season>\d+)@?x@?(?P<episode>\d+)') \
        .regex(r'(?P<episodeSeparator>x|-|\+|&)(?P<episode>\d+)').repeater('*') \
        .close() \
        .chain() \
        .defaults(children=True, private_parent=True) \
        .regex(r'S(?P<season>\d+)@?(?:xE|Ex|E|x)@?(?P<episode>\d+)') \
        .regex(r'(?:(?P<episodeSeparator>xE|Ex|E|x|-|\+|&)(?P<episode>\d+))').repeater('*') \
        .close() \
        .chain() \
        .defaults(children=True, private_parent=True) \
        .regex(r'S(?P<season>\d+)') \
        .regex(r'(?P<seasonSeparator>S|-|\+|&)(?P<season>\d+)').repeater('*')

    matches = rebulk.matches("test-01x02-03")
    assert len(matches) == 3

    assert matches[0].name == 'season'
    assert matches[0].value == 1

    assert matches[1].name == 'episode'
    assert matches[1].value == 2

    assert matches[2].name == 'episode'
    assert matches[2].value == 3

    matches = rebulk.matches("test-S01E02-03")

    assert len(matches) == 3
    assert matches[0].name == 'season'
    assert matches[0].value == 1

    assert matches[1].name == 'episode'
    assert matches[1].value == 2

    assert matches[2].name == 'episode'
    assert matches[2].value == 3

    matches = rebulk.matches("test-S01-02-03-04")

    assert len(matches) == 4
    assert matches[0].name == 'season'
    assert matches[0].value == 1

    assert matches[1].name == 'season'
    assert matches[1].value == 2

    assert matches[2].name == 'season'
    assert matches[2].value == 3

    assert matches[3].name == 'season'
    assert matches[3].value == 4


def test_matches_4():
    seps_surround = partial(chars_surround, " ")

    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.defaults(validate_all=True, children=True)
    rebulk.defaults(private_names=['episodeSeparator', 'seasonSeparator'], private_parent=True)

    rebulk.chain(validator={'__parent__': seps_surround}, formatter={'episode': int, 'version': int}) \
        .defaults(formatter={'episode': int, 'version': int}) \
        .regex(r'e(?P<episode>\d{1,4})') \
        .regex(r'v(?P<version>\d+)').repeater('?') \
        .regex(r'(?P<episodeSeparator>e|x|-)(?P<episode>\d{1,4})').repeater('*')

    matches = rebulk.matches("Some Series E01E02E03")
    assert len(matches) == 3

    assert matches[0].value == 1
    assert matches[1].value == 2
    assert matches[2].value == 3


def test_matches_5():
    seps_surround = partial(chars_surround, " ")

    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)

    rebulk.chain(private_names=['episodeSeparator', 'seasonSeparator'], validate_all=True,
                 validator={'__parent__': seps_surround}, children=True, private_parent=True,
                 formatter={'episode': int, 'version': int}) \
        .defaults(children=True, private_parent=True) \
        .regex(r'e(?P<episode>\d{1,4})') \
        .regex(r'v(?P<version>\d+)').repeater('?') \
        .regex(r'(?P<episodeSeparator>e|x|-)(?P<episode>\d{1,4})').repeater('{2,3}')

    matches = rebulk.matches("Some Series E01E02E03")
    assert len(matches) == 3

    matches = rebulk.matches("Some Series E01E02")
    assert len(matches) == 0

    matches = rebulk.matches("Some Series E01E02E03E04E05E06")  # Parent can't be validated, so no results at all
    assert len(matches) == 0


def test_matches_6():
    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.defaults(private_names=['episodeSeparator', 'seasonSeparator'], validate_all=True,
                    validator=None, children=True, private_parent=True)

    rebulk.chain(formatter={'episode': int, 'version': int}) \
        .defaults(children=True, private_parent=True) \
        .regex(r'e(?P<episode>\d{1,4})') \
        .regex(r'v(?P<version>\d+)').repeater('?') \
        .regex(r'(?P<episodeSeparator>e|x|-)(?P<episode>\d{1,4})').repeater('{2,3}')

    matches = rebulk.matches("Some Series E01E02E03")
    assert len(matches) == 3

    matches = rebulk.matches("Some Series E01E02")
    assert len(matches) == 0

    matches = rebulk.matches("Some Series E01E02E03E04E05E06")  # No validator on parent, so it should give 4 episodes.
    assert len(matches) == 4


def test_matches_7():
    seps_surround = partial(chars_surround, ' .-/')
    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.defaults(children=True, private_parent=True)

    rebulk.chain(). \
        regex(r'S(?P<season>\d+)', validate_all=True, validator={'__parent__': seps_surround}). \
        regex(r'[ -](?P<season>\d+)', validator=seps_surround).repeater('*')

    matches = rebulk.matches("Some S01")
    assert len(matches) == 1
    matches[0].value = 1

    matches = rebulk.matches("Some S01-02")
    assert len(matches) == 2
    matches[0].value = 1
    matches[1].value = 2

    matches = rebulk.matches("programs4/Some S01-02")
    assert len(matches) == 2
    matches[0].value = 1
    matches[1].value = 2

    matches = rebulk.matches("programs4/SomeS01middle.S02-03.andS04here")
    assert len(matches) == 2
    matches[0].value = 2
    matches[1].value = 3

    matches = rebulk.matches("Some 02.and.S04-05.here")
    assert len(matches) == 2
    matches[0].value = 4
    matches[1].value = 5


def test_chain_breaker():
    def chain_breaker(matches):
        seasons = matches.named('season')
        if len(seasons) > 1:
            if seasons[-1].value - seasons[-2].value > 10:
                return True
        return False

    seps_surround = partial(chars_surround, ' .-/')
    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.defaults(children=True, private_parent=True, formatter={'season': int})

    rebulk.chain(chain_breaker=chain_breaker). \
        regex(r'S(?P<season>\d+)', validate_all=True, validator={'__parent__': seps_surround}). \
        regex(r'[ -](?P<season>\d+)', validator=seps_surround).repeater('*')

    matches = rebulk.matches("Some S01-02-03-50-51")
    assert len(matches) == 3
    matches[0].value = 1
    matches[1].value = 2
    matches[2].value = 3


def test_chain_breaker_defaults():
    def chain_breaker(matches):
        seasons = matches.named('season')
        if len(seasons) > 1:
            if seasons[-1].value - seasons[-2].value > 10:
                return True
        return False

    seps_surround = partial(chars_surround, ' .-/')
    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.defaults(chain_breaker=chain_breaker, children=True, private_parent=True, formatter={'season': int})

    rebulk.chain(). \
        regex(r'S(?P<season>\d+)', validate_all=True, validator={'__parent__': seps_surround}). \
        regex(r'[ -](?P<season>\d+)', validator=seps_surround).repeater('*')

    matches = rebulk.matches("Some S01-02-03-50-51")
    assert len(matches) == 3
    matches[0].value = 1
    matches[1].value = 2
    matches[2].value = 3


def test_chain_breaker_defaults2():
    def chain_breaker(matches):
        seasons = matches.named('season')
        if len(seasons) > 1:
            if seasons[-1].value - seasons[-2].value > 10:
                return True
        return False

    seps_surround = partial(chars_surround, ' .-/')
    rebulk = Rebulk()
    rebulk.regex_defaults(flags=re.IGNORECASE)
    rebulk.chain_defaults(chain_breaker=chain_breaker)
    rebulk.defaults(children=True, private_parent=True, formatter={'season': int})

    rebulk.chain(). \
        regex(r'S(?P<season>\d+)', validate_all=True, validator={'__parent__': seps_surround}). \
        regex(r'[ -](?P<season>\d+)', validator=seps_surround).repeater('*')

    matches = rebulk.matches("Some S01-02-03-50-51")
    assert len(matches) == 3
    matches[0].value = 1
    matches[1].value = 2
    matches[2].value = 3


def test_group_by_match_index_with_unsorted_data():
    """
    The groupby function requires pre-sorted data, so _group_by_match_index
    must sort matches by match_index before grouping.
    """
    
    # Create mock matches with unsorted match_index values
    match1 = Match(0, 5, value='a', name='test')
    match1.match_index = 2
    
    match2 = Match(6, 10, value='b', name='test')
    match2.match_index = 0
    
    match3 = Match(11, 15, value='c', name='test')
    match3.match_index = 1
    
    match4 = Match(16, 20, value='d', name='test')
    match4.match_index = 2
    
    # Create unsorted matches list
    unsorted_matches = [match1, match2, match3, match4]
    
    # Call _group_by_match_index with unsorted data
    grouped = Chain._group_by_match_index(unsorted_matches)
    
    # Verify grouping is correct despite unsorted input
    assert 0 in grouped
    assert 1 in grouped
    assert 2 in grouped
    
    assert len(grouped[0]) == 1
    assert grouped[0][0] == match2
    
    assert len(grouped[1]) == 1
    assert grouped[1][0] == match3
    
    assert len(grouped[2]) == 2
    assert grouped[2][0] == match1
    assert grouped[2][1] == match4

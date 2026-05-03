import pytest
from timetable.parser import parse_period


def test_dash_range():
    assert parse_period("3-5") == {3, 4, 5}


def test_tilde_range():
    assert parse_period("3~5") == {3, 4, 5}


def test_single_period():
    assert parse_period("7") == {7}


def test_with_spaces():
    assert parse_period("3 - 5") == {3, 4, 5}


def test_invalid_raises():
    with pytest.raises(ValueError):
        parse_period("abc")

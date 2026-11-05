# tests/parser/test_sentinels.py

from py1cORM.parser.sentinels import NotLoaded


def test_returns_readable_repr_when_value_is_not_loaded():
    assert repr(NotLoaded) == 'NotLoaded'


def test_is_falsy_when_value_is_not_loaded():
    assert bool(NotLoaded) is False

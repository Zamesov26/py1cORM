# tests/parser/test_sentinels.py

from py1cORM.parser.sentinels import NotLoaded


def test_notloaded_repr():
    assert repr(NotLoaded) == 'NotLoaded'


def test_notloaded_bool():
    assert bool(NotLoaded) is False

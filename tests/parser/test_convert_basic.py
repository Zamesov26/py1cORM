from datetime import datetime
from uuid import UUID

from py1cORM.parser.convert import ZERO_UUID, convert


def test_uuid_conversion():
    val = '550e8400-e29b-41d4-a716-446655440000'
    result = convert(val, UUID)
    assert isinstance(result, UUID)


def test_zero_uuid_to_none():
    result = convert(ZERO_UUID, UUID)
    assert result is None


def test_optional_uuid():
    result = convert(ZERO_UUID, UUID | None)
    assert result is None


def test_datetime_conversion():
    val = '2024-01-01T10:00:00'
    result = convert(val, datetime)
    assert isinstance(result, datetime)


def test_zero_datetime_to_none():
    val = '0001-01-01T00:00:00'
    result = convert(val, datetime)
    assert result is None


def test_list_uuid():
    val = [
        '550e8400-e29b-41d4-a716-446655440000',
        ZERO_UUID,
    ]
    result = convert(val, list[UUID])
    assert isinstance(result[0], UUID)
    assert result[1] is None

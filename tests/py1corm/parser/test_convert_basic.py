from datetime import datetime
from uuid import UUID

from py1cORM.parser.convert import ZERO_UUID, convert


def test_returns_uuid_when_annotation_is_uuid():
    val = '550e8400-e29b-41d4-a716-446655440000'
    result = convert(val, UUID)
    assert isinstance(result, UUID)


def test_returns_none_when_uuid_is_zero():
    result = convert(ZERO_UUID, UUID)
    assert result is None


def test_returns_uuid_when_annotation_is_optional_uuid():
    result = convert(ZERO_UUID, UUID | None)
    assert result is None


def test_returns_datetime_when_annotation_is_datetime():
    val = '2024-01-01T10:00:00'
    result = convert(val, datetime)
    assert isinstance(result, datetime)


def test_returns_none_when_datetime_has_zero_year():
    val = '0001-01-01T00:00:00'
    result = convert(val, datetime)
    assert result is None


def test_converts_each_item_when_annotation_is_uuid_list():
    val = [
        '550e8400-e29b-41d4-a716-446655440000',
        ZERO_UUID,
    ]
    result = convert(val, list[UUID])
    assert isinstance(result[0], UUID)
    assert result[1] is None

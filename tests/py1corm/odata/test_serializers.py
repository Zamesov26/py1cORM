from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from py1cORM.odata.serializers import serialize_value


def test_quotes_value_when_serializing_string():
    assert serialize_value('abc') == "'abc'"


def test_escapes_quote_when_serializing_string():
    assert serialize_value("O'Brian") == "'O''Brian'"


def test_returns_decimal_literal_when_serializing_integer():
    assert serialize_value(10) == '10'


def test_returns_lowercase_literal_when_serializing_boolean():
    assert serialize_value(True) == 'true'
    assert serialize_value(False) == 'false'


def test_returns_null_literal_when_serializing_none():
    assert serialize_value(None) == 'null'


def test_returns_guid_literal_when_serializing_uuid():
    uid = UUID('845660ff-365e-11ec-aa35-ac1f6bd30991')
    assert serialize_value(uid) == f"guid'{uid}'"


def test_returns_datetime_literal_when_serializing_datetime():
    dt = datetime(2024, 1, 1, 10, 0, 0)
    assert serialize_value(dt) == "datetime'2024-01-01T10:00:00'"


def test_removes_timezone_when_serializing_aware_datetime():
    dt = datetime(2026, 2, 28, 15, 58, 39, tzinfo=UTC)

    result = serialize_value(dt)

    assert result == "datetime'2026-02-28T15:58:39'"


def test_preserves_precision_when_serializing_decimal():
    assert serialize_value(Decimal('10.5')) == '10.5'

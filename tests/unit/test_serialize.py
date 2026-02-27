from datetime import datetime
from decimal import Decimal
from uuid import UUID

from PyOData1C.odata.serializers import serialize_value


def test_serialize_string():
    assert serialize_value("abc") == "'abc'"


def test_serialize_string_escape():
    assert serialize_value("O'Brian") == "'O''Brian'"


def test_serialize_int():
    assert serialize_value(10) == "10"


def test_serialize_bool():
    assert serialize_value(True) == "true"
    assert serialize_value(False) == "false"


def test_serialize_none():
    assert serialize_value(None) == "null"


def test_serialize_uuid():
    uid = UUID("845660ff-365e-11ec-aa35-ac1f6bd30991")
    assert serialize_value(uid) == f"guid'{uid}'"


def test_serialize_datetime():
    dt = datetime(2024, 1, 1, 10, 0, 0)
    assert serialize_value(dt) == "datetime'2024-01-01T10:00:00'"


def test_serialize_decimal():
    assert serialize_value(Decimal("10.5")) == "10.5"
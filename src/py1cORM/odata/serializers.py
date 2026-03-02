from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


def _serialize_none(_):
    return 'null'


def _serialize_bool(value: bool):
    return 'true' if value else 'false'


def _serialize_number(value):
    return str(value)


def _serialize_decimal(value: Decimal):
    return str(value)


def _serialize_uuid(value: UUID):
    return f"guid'{value}'"


def _serialize_datetime(value: datetime):
    iso = value.replace(microsecond=0).isoformat()
    return f"datetime'{iso}'"


def _serialize_date(value: date):
    return f"date'{value.isoformat()}'"


def _serialize_str(value: str):
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _serialize_collection(value):
    serialized = ', '.join(serialize_value(v) for v in value)
    return f'({serialized})'


_TYPE_SERIALIZERS = {
    type(None): _serialize_none,
    bool: _serialize_bool,
    int: _serialize_number,
    float: _serialize_number,
    Decimal: _serialize_decimal,
    UUID: _serialize_uuid,
    datetime: _serialize_datetime,
    date: _serialize_date,
    str: _serialize_str,
}


def serialize_value(value):
    if hasattr(value, 'to_odata'):
        return value.to_odata()

    if isinstance(value, (list, tuple, set)):
        return _serialize_collection(value)

    serializer = _TYPE_SERIALIZERS.get(type(value))
    if serializer:
        return serializer(value)

    raise TypeError(f'Unsupported type for OData serialization: {type(value)}')

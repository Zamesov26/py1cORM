from datetime import datetime
from types import UnionType
from typing import Union, get_args, get_origin
from uuid import UUID

from dateutil.parser import isoparse

from py1cORM.models.base import ODataModel

ZERO_UUID = '00000000-0000-0000-0000-000000000000'


def convert(value, annotation):
    if value is None:
        return None

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[T]
    if origin in (Union, UnionType) and type(None) in args:
        real_type = next(t for t in args if t is not type(None))
        return convert(value, real_type)

    # list[T]
    if origin is list:
        inner = args[0]
        return [convert(v, inner) for v in value]

    # UUID
    if annotation is UUID:
        if value == ZERO_UUID:
            return None
        return UUID(value)

    # datetime
    if annotation is datetime:
        dt = isoparse(value)
        if dt.year <= 1:
            return None
        return dt

    if isinstance(annotation, type) and issubclass(annotation, ODataModel):
        return annotation.from_raw(value)

    # простые типы
    try:
        return annotation(value)
    except Exception:
        return value

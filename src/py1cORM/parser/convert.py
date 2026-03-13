from datetime import datetime
from types import UnionType
from typing import Union, get_args, get_origin
from uuid import UUID

from dateutil.parser import isoparse

from py1cORM.models.base import ODataModel

ZERO_UUID = '00000000-0000-0000-0000-000000000000'


def _unwrap_optional(annotation):
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, UnionType) and type(None) in args:
        return next(t for t in args if t is not type(None))

    return None


def _convert_list(value, annotation):
    args = get_args(annotation)
    inner = args[0]

    if not isinstance(value, list):
        return []

    return [convert(v, inner) for v in value]


def _convert_uuid(value):
    if value == ZERO_UUID:
        return None
    return UUID(value)


def _convert_datetime(value):
    dt = isoparse(value)

    if dt.year <= 1:
        return None

    return dt


def _is_model(annotation):
    return isinstance(annotation, type) and issubclass(annotation, ODataModel)


def _convert_model(value, annotation):
    if not isinstance(value, dict):
        return None

    return annotation.from_raw(value)


def _convert_scalar(value, annotation):
    try:
        return annotation(value)
    except Exception:
        return value


def convert(value, annotation):
    if value is None:
        return None

    optional = _unwrap_optional(annotation)
    if optional is not None:
        return convert(value, optional)

    origin = get_origin(annotation)

    if origin is list:
        return _convert_list(value, annotation)

    if annotation is UUID:
        return _convert_uuid(value)

    if annotation is datetime:
        return _convert_datetime(value)

    if _is_model(annotation):
        return _convert_model(value, annotation)

    return _convert_scalar(value, annotation)

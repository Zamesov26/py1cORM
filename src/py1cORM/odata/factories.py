"""Фабрики декларативных полей с настройками по умолчанию для OData."""

from py1cORM.models.fields import Embedded as _Embedded
from py1cORM.models.fields import Field as _Field
from py1cORM.models.fields import ForeignKey as _ForeignKey


def Field(*, alias=None, odata_name=None, auto_expand=False, default=None):
    """Создать скалярное поле модели OData."""
    return _Field(
        alias=alias,
        odata_name=odata_name,
        auto_expand=auto_expand,
        default=default,
    )


def Embedded(
    *,
    model,
    alias=None,
    odata_name=None,
    auto_expand=False,
    default=None,
):
    """Создать поле встроенной структуры или коллекции."""
    return _Embedded(
        model=model,
        alias=alias,
        odata_name=odata_name,
        auto_expand=auto_expand,
        default=default,
    )


def ForeignKey(
    *,
    model,
    key_field,
    alias=None,
    odata_name=None,
    auto_expand=True,
    default=None,
):
    """Создать поле внешнего ключа с автоматическим раскрытием по умолчанию."""
    return _ForeignKey(
        model=model,
        key_field=key_field,
        alias=alias,
        odata_name=odata_name,
        auto_expand=auto_expand,
        default=default,
    )

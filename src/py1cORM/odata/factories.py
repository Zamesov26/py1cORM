"""Фабрики декларативных полей с настройками по умолчанию для OData."""

from py1cORM.models.fields import Embedded as _Embedded
from py1cORM.models.fields import Field as _Field
from py1cORM.models.fields import Relationship as _Relationship


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


def Relationship(
    *,
    model,
    alias=None,
    odata_name=None,
    auto_expand=True,
    default=None,
):
    """Создать связь с автоматическим раскрытием по умолчанию."""
    return _Relationship(
        model=model,
        alias=alias,
        odata_name=odata_name,
        auto_expand=auto_expand,
        default=default,
    )

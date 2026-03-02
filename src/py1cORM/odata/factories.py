from py1cORM.models.fields import Embedded as _Embedded
from py1cORM.models.fields import Field as _Field
from py1cORM.models.fields import ForeignKey as _ForeignKey


def Field(
    *, alias=None, odata_name=None, auto_select=True, auto_expand=False, default=None
):
    return _Field(
        alias=alias,
        odata_name=odata_name,
        auto_select=auto_select,
        auto_expand=auto_expand,
        default=default,
    )


def Embedded(
    *,
    model,
    alias=None,
    odata_name=None,
    auto_select=True,
    auto_expand=False,
    default=None,
):
    return _Embedded(
        model=model,
        alias=alias,
        odata_name=odata_name,
        auto_select=auto_select,
        auto_expand=auto_expand,
        default=default,
    )


def ForeignKey(
    *,
    model,
    key_field,
    alias=None,
    odata_name=None,
    auto_select=True,
    auto_expand=True,
    default=None,
):
    return _ForeignKey(
        model=model,
        key_field=key_field,
        alias=alias,
        odata_name=odata_name,
        auto_select=auto_select,
        auto_expand=auto_expand,
        default=default,
    )

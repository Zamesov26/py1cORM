from py1cORM.odata.fields import ScalarField, EmbeddedField, ForeignKeyField


def Field(*, alias=None, odata_name=None, auto_select=True, default=None, **kwargs):
    return ScalarField(
        alias=alias,
        odata_name=odata_name,
        auto_select=auto_select,
        default=default,
        **kwargs
    )

def Embedded(*, model, alias=None, default=None, **kwargs):
    return EmbeddedField(
        model=model,
        alias=alias,
        default=default,
        **kwargs
    )

def ForeignKey(*, model, alias=None, default=None, **kwargs):
    return ForeignKeyField(
        model=model,
        alias=alias,
        default=default,
        **kwargs
    )
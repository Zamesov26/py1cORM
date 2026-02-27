from py1cORM.odata.fields import ScalarField, EmbeddedField, ForeignKeyField


def Field(*, alias=None, odata_name=None, auto_select=True, **kwargs):
    return ScalarField(
        alias=alias,
        odata_name=odata_name,
        auto_select=auto_select,
        default=None,
        **kwargs
    )


def Embedded(*, model, alias=None, odata_name=None, auto_select=True, auto_expand=False, **kwargs):
    return EmbeddedField(model=model, alias=alias, odata_name=odata_name, auto_select=auto_select, auto_expand=auto_expand, **kwargs)

def ForeignKey(*, model, alias=None, odata_name=None, auto_select=True, auto_expand=False, key_name=None, **kwargs):
    return ForeignKeyField(model=model, key_name=key_name, alias=alias, odata_name=odata_name, auto_select=auto_select, auto_expand=auto_expand, **kwargs)
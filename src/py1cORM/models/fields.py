from py1cORM.odata.fields import FieldRef


class Field:
    is_relation = False
    is_embedded = False
    is_foreign_key = False

    def __init__(
        self,
        *,
        alias: str | None = None,
        odata_name: str | None = None,
        auto_select: bool = True,
        auto_expand: bool = False,
        default=None,
    ):
        self.alias = alias
        self.odata_name = odata_name or alias
        self.auto_select = auto_select
        self.auto_expand = auto_expand
        self.default = default

        self.model = None
        self.attr_name = None
        self.annotation = None

    def bind(self, model, attr_name: str, annotation):
        self.model = model
        self.attr_name = attr_name
        self.annotation = annotation

        if not self.odata_name:
            self.odata_name = self.alias or attr_name

        return self

    def ref(self):
        return FieldRef(self.model, self)

    def get_related_model(self):
        raise AttributeError(f"Field '{self.attr_name}' is not a relation")


class Embedded(Field):
    is_relation = True
    is_embedded = True

    def __init__(self, *, model: type, expand_only=False, **kwargs):
        super().__init__(**kwargs)
        self.embedded_model = model
        self.expand_only = expand_only

    def get_related_model(self):
        return self.embedded_model


class ForeignKey(Field):
    is_relation = True
    is_foreign_key = True

    def __init__(self, *, model: type, key_field: str, **kwargs):
        super().__init__(**kwargs)
        self.related_model = model
        self.key_field = key_field

    def get_related_model(self):
        return self.related_model

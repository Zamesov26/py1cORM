from pydantic.fields import FieldInfo

from py1cORM.odata.expressions import BinExpr, FuncExpr


class ODataFieldInfo(FieldInfo):
    is_relation = False
    
    def __init__(
        self,
        *,
        odata_name: str | None = None,
        auto_select: bool = True,
        auto_expand: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.odata_name = odata_name or self.alias
        self.auto_select = auto_select
        self.auto_expand = auto_expand

        # будет проставлено метаклассом модели:
        self.model = None
        self.attr_name = None

    def bind(self, model, attr_name: str):
        self.model = model
        self.attr_name = attr_name
        if not self.odata_name:
            self.odata_name = self.alias or attr_name
        return self

    # ссылка на поле для DSL
    def ref(self):
        return FieldRef(self.model, self)

    def get_related_model(self):
        raise AttributeError(
            f"Field '{self.attr_name}' is not a relation"
        )
    
    
class ScalarField(ODataFieldInfo):
    pass

class EmbeddedField(ODataFieldInfo):
    is_relation = True
    
    def __init__(self, *, model: type, **kwargs):
        super().__init__(**kwargs)
        self.embedded_model = model
        
    def get_related_model(self):
        return self.embedded_model


class ForeignKeyField(ODataFieldInfo):
    is_relation = True
    
    def __init__(self, *, model: type, key_name: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.related_model = model
        self.key_name = key_name  # если нужно Ref_Key отдельно
        
    def get_related_model(self):
        return self.related_model


class FieldRef:
    def __init__(self, model, field_or_fields):
        self.model = model
        
        # если передали один field — превращаем в список
        if isinstance(field_or_fields, list):
            self.fields = field_or_fields
        else:
            self.fields = [field_or_fields]
    
    @property
    def field(self):
        return self.fields[-1]
    
    @property
    def path(self):
        return "/".join(
            f.odata_name for f in self.fields
        )
    
    def __getattr__(self, item):
        field = self.field
        
        if not field.is_relation:
            raise AttributeError(
                f"Cannot traverse scalar field '{field.attr_name}'"
            )
        
        target_model = field.get_related_model()
        
        next_field = target_model.model_fields.get(item)
        if not next_field:
            raise AttributeError(
                f"{item} not found in {target_model.__name__}"
            )
        
        return FieldRef(
            target_model,
            self.fields + [next_field],
            )

    
    def __eq__(self, other):
        return BinExpr(self, "eq", other)
    
    def __ne__(self, other):
        return BinExpr(self, "ne", other)
    
    def __gt__(self, other):
        return BinExpr(self, "gt", other)
    
    def __lt__(self, other):
        return BinExpr(self, "lt", other)
    
    def __ge__(self, other):
        return BinExpr(self, "ge", other)
    
    def __le__(self, other):
        return BinExpr(self, "le", other)





def like(field: FieldRef, pattern: str):
    return BinExpr(field, "like", pattern)


def contains(field: FieldRef, value: str):
    return FuncExpr("contains", field, value)

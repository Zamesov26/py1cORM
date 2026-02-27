from dataclasses import dataclass

from py1cORM.odata.fields import FieldRef, contains
from py1cORM.odata.serializers import serialize_value
from py1cORM.odata.utils import field_to_path, order_to_odata
from py1cORM.odata.models import ODataModel
from py1cORM.odata.expressions import BinExpr, AndExpr, Expr, FuncExpr, RawExpr, AND

LOOKUP_MAP = {
    "eq": "eq",
    "ne": "ne",
    "gt": "gt",
    "ge": "ge",
    "lt": "lt",
    "le": "le",
}

def kwargs_to_expr(model, kwargs: dict):
    expressions = []
    
    for key, value in kwargs.items():
        parts = key.split("__")
        
        field_name = parts[0]
        lookup = parts[1] if len(parts) > 1 else "eq"
        
        field = model.__pydantic_fields__.get(field_name)
        if not field:
            raise ValueError(f"Unknown field: {field_name}")
        
        field_ref = FieldRef(model, field)
        
        if lookup == "eq":
            expr = BinExpr(field_ref, "eq", value)
        
        elif lookup == "contains":
            expr = FuncExpr("contains", field_ref, value)
        
        elif lookup == "isnull":
            if value:
                expr = BinExpr(field_ref, "eq", None)
            else:
                expr = BinExpr(field_ref, "ne", None)
        
        else:
            raise ValueError(f"Unsupported lookup: {lookup}")
        
        expressions.append(expr)
    
    if len(expressions) == 1:
        return expressions[0]
    
    return AndExpr(*expressions)


@dataclass
class QuerySpec:
    select: list[str] | None = None
    expand: list[str] | None = None
    filter: str | None = None
    orderby: list[str] | None = None
    top: int | None = None
    skip: int | None = None
    count: bool | None = None
    
class QuerySet:
    def __init__(self, client, model: type[ODataModel], spec: QuerySpec | None = None):
        self.client = client
        self.model = model
        self.spec = spec or QuerySpec()
        self._explicit_select = False

    def clone(self):
        return QuerySet(self.client, self.model, QuerySpec(**vars(self.spec)))

    def select(self, *fields):
        qs = self.clone()
        qs._explicit_select = True
        qs.spec.select = [field_to_path(self.model, f) for f in fields]
        return qs

    def expand(self, *fields):
        qs = self.clone()
        qs.spec.expand = [field_to_path(self.model, f) for f in fields]
        return qs

    def filter(self, *conditions):
        for condition in conditions:
            if isinstance(condition, Expr):
                self.spec.filter = condition.to_odata()
            elif isinstance(condition, str):
                self.spec.filter = condition
            else:
                raise TypeError("Unsupported filter argument")
        return self


    def order_by(self, *fields):
        qs = self.clone()
        qs.spec.orderby = [order_to_odata(self.model, f) for f in fields]
        return qs

    def paginate(self, *, top: int | None = None, skip: int | None = None):
        qs = self.clone()
        qs.spec.top = top
        qs.spec.skip = skip
        return qs

    def _finalize_defaults(self):
        # select defaults
        if not self._explicit_select and self.spec.select is None:
            self.spec.select = [
                f.odata_name for f in self.model.model_fields.values()
                if f.auto_select
            ]
        # expand defaults
        if self.spec.expand is None:
            self.spec.expand = [
                f.odata_name for f in self.model.model_fields.values()
                if f.auto_expand
            ]

    def all(self):
        self._finalize_defaults()
        data = self.client.get_collection(self.model.Meta.entity_name, self.spec)
        return [self.model.model_validate(item) for item in data]

    def get(self, **kwargs):
        # kwargs можно конвертировать в AND(...) автоматически
        expr = kwargs_to_expr(self.model, kwargs)
        items = self.filter(expr).paginate(top=2).all()
        if not items:
            raise LookupError("Not found")
        if len(items) > 1:
            raise LookupError("Multiple objects")
        return items[0]
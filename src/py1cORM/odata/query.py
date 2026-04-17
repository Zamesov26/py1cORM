from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from py1cORM.odata.expressions import AndExpr, BinExpr, Expr, FuncExpr
from py1cORM.odata.fields import FieldRef
from py1cORM.odata.utils import field_to_path, order_to_odata

if TYPE_CHECKING:
    from py1cORM.models.base import ODataModel

LOOKUP_MAP = {
    'eq': 'eq',
    'ne': 'ne',
    'gt': 'gt',
    'ge': 'ge',
    'lt': 'lt',
    'le': 'le',
}


def kwargs_to_expr(model, kwargs: dict):
    expressions = []

    for key, value in kwargs.items():
        parts = key.split('__')

        field_name = parts[0]
        lookup = parts[1] if len(parts) > 1 else 'eq'

        field = model._fields.get(field_name)
        if not field:
            raise ValueError(f'Unknown field: {field_name}')

        field_ref = FieldRef(model, field)

        if lookup == 'eq':
            expr = BinExpr(field_ref, 'eq', value)

        elif lookup == 'contains':
            expr = FuncExpr('contains', field_ref, value)

        elif lookup == 'isnull':
            if value:
                expr = BinExpr(field_ref, 'eq', None)
            else:
                expr = BinExpr(field_ref, 'ne', None)

        else:
            raise ValueError(f'Unsupported lookup: {lookup}')

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


T = TypeVar("T", bound="ODataModel")

class QuerySet[T]:
    def __init__(self, client, model: type[T], spec: QuerySpec | None = None):
        self.client = client
        self.model = model
        self.spec = spec or QuerySpec()
        self._explicit_select = False

    def clone(self) -> QuerySet[T]:
        return QuerySet(self.client, self.model, QuerySpec(**vars(self.spec)))

    def select(self, *fields):
        qs = self.clone()
        qs._explicit_select = True
        qs.spec.select = [field_to_path(self.model, f) for f in fields]
        return qs

    def expand(self, *fields) -> QuerySet[T]:
        qs = self.clone()
        qs.spec.expand = [field_to_path(self.model, f) for f in fields]
        return qs

    # TODO: проверить возможно тут не правильная логика
    def filter(self, *conditions) -> QuerySet[T]:
        for condition in conditions:
            if isinstance(condition, Expr):
                qs = self.clone()
                qs.spec.filter = condition.to_odata()
                return qs
            elif isinstance(condition, str):
                self.spec.filter = condition
            else:
                raise TypeError('Unsupported filter argument')
        return self

    def order_by(self, *fields) -> QuerySet[T]:
        qs = self.clone()
        qs.spec.orderby = [order_to_odata(self.model, f) for f in fields]
        return qs

    def paginate(self, *, top: int | None = None, skip: int | None = None) -> QuerySet[T]:
        qs = self.clone()
        qs.spec.top = top
        qs.spec.skip = skip
        return qs

    def _finalize_defaults(self):
        # TODO если select не указан грузим все поля(не указываем select)
        # TODO: возможно нужно подумать над какой-то надстрой типа only_model_fields
        if not self._explicit_select and self.spec.select is None:
            self.spec.select = [
                f.odata_name for f in self.model._fields.values() if f.auto_select
            ]

        # если select указан → гарантируем pk
        if self._explicit_select:
            pk_name = getattr(self.model.Meta, 'pk', None)

            if pk_name:
                pk_field = self.model._fields[pk_name]
                pk_odata = pk_field.odata_name

                if pk_odata not in self.spec.select:
                    self.spec.select.append(pk_odata)

    def all(self) -> list[T]:
        self._finalize_defaults()
        data = self.client.get_collection(self.model.Meta.entity_name, self.spec)
        return [self.model.from_raw(item) for item in data]

    def batched(self, batch_size: int = 100) -> Iterable[list[T]]:
        skip = 0

        while True:
            batch = self.paginate(top=batch_size, skip=skip).all()
            if not batch:
                break

            yield batch
            skip += batch_size

    def get(self, **kwargs) -> T:
        # kwargs можно конвертировать в AND(...) автоматически
        expr = kwargs_to_expr(self.model, kwargs)
        items = self.filter(expr).paginate(top=2).all()
        if not items:
            raise LookupError('Not found')
        if len(items) > 1:
            raise LookupError('Multiple objects')
        return items[0]

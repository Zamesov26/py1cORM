"""Спецификация и ленивое построение запросов к коллекциям OData."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from time import sleep
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
    """Преобразовать именованные lookup-условия в выражение OData."""
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

        elif lookup == 'startswith':
            expr = FuncExpr('startswith', field_ref, value)

        elif lookup == 'endswith':
            expr = FuncExpr('endswith', field_ref, value)

        else:
            raise ValueError(f'Unsupported lookup: {lookup}')

        expressions.append(expr)

    if len(expressions) == 1:
        return expressions[0]

    return AndExpr(*expressions)


@dataclass
class QuerySpec:
    """Параметры одного запроса к коллекции OData."""

    select: list[str] | None = None
    expand: list[str] | None = None
    filter: str | None = None
    orderby: list[str] | None = None
    top: int | None = None
    skip: int | None = None
    count: bool | None = None


T = TypeVar('T', bound='ODataModel')


class QuerySet[T]:
    """Построитель запросов и загрузчик сущностей указанной модели."""

    def __init__(self, client, model: type[T], spec: QuerySpec | None = None):
        self.client = client
        self.model = model
        self.spec = spec or QuerySpec()

    def clone(self) -> QuerySet[T]:
        """Создать независимую копию текущей спецификации запроса."""
        return QuerySet(self.client, self.model, QuerySpec(**vars(self.spec)))

    def select(self, *fields):
        """Ограничить ответ указанными полями модели."""
        qs = self.clone()
        qs.spec.select = [field_to_path(self.model, f) for f in fields]
        return qs

    def expand(self, *fields) -> QuerySet[T]:
        """Добавить раскрытие указанных связей через ``$expand``."""
        qs = self.clone()
        qs.spec.expand = [field_to_path(self.model, f) for f in fields]
        return qs

    # TODO: проверить возможно тут не правильная логика
    # NB: Подразумевается, что все фильтры образуют один объект(вложены друг в друга)
    # TODO: нужно объединить их всех с помощью AND
    def filter(self, *conditions) -> QuerySet[T]:
        """Добавить выражение или готовую строку фильтра OData."""
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
        """Задать порядок результатов по полям и направлениям сортировки."""
        qs = self.clone()
        qs.spec.orderby = [order_to_odata(self.model, f) for f in fields]
        return qs

    def paginate(
        self, *, top: int | None = None, skip: int | None = None
    ) -> QuerySet[T]:
        """Задать ограничение и смещение коллекции."""
        qs = self.clone()
        qs.spec.top = top
        qs.spec.skip = skip
        return qs

    def _finalize_defaults(self):
        if self.spec.select is not None:
            pk_name = getattr(self.model.Meta, 'pk', None)

            if pk_name:
                pk_field = self.model._fields[pk_name]
                pk_odata = pk_field.odata_name

                if pk_odata not in self.spec.select:
                    self.spec.select.append(pk_odata)

    def all(self) -> list[T]:
        """Выполнить запрос и преобразовать ответ в сущности модели."""
        self._finalize_defaults()
        data = self.client.get_collection(self.model.Meta.entity_name, self.spec)
        return [self.model.from_raw(item) for item in data]

    def batched(self, batch_size: int = 100, delay: float = 0) -> Iterable[list[T]]:
        """Последовательно загружать страницы с паузой между запросами.

        Args:
            batch_size: Максимальное количество сущностей в одном запросе.
            delay: Пауза между соседними запросами в секундах.

        Yields:
            Очередная непустая страница сущностей.

        Raises:
            ValueError: Передана отрицательная длительность паузы.
        """
        if delay < 0:
            raise ValueError('Delay cannot be negative')

        skip = 0
        is_first_request = True

        while True:
            if not is_first_request and delay:
                sleep(delay)

            batch = self.paginate(top=batch_size, skip=skip).all()
            is_first_request = False

            if not batch:
                break

            yield batch
            skip += batch_size

    def get(self, **kwargs):
        """Получить единственную сущность по именованным условиям.

        Raises:
            LookupError: Сущность не найдена или найдено несколько сущностей.
        """
        qs = self

        if kwargs:
            qs = qs.filter(kwargs_to_expr(self.model, kwargs))

        items = qs.paginate(top=2).all()

        if not items:
            raise LookupError('Not found')
        if len(items) > 1:
            raise LookupError('Multiple objects')

        return items[0]

"""Ссылки на поля моделей для путей, сравнений и функций OData."""

from __future__ import annotations

from collections.abc import Iterable
from typing import overload

from py1cORM.odata.expressions import BinExpr, FuncExpr, InExpr


class FieldRef[ModelT, T]:
    """Ссылка на поле или цепочку связанных полей модели OData."""

    def __init__(self, model, field_or_fields):
        self.model = model

        if isinstance(field_or_fields, list):
            self.fields = field_or_fields
        else:
            self.fields = [field_or_fields]

    @property
    def field(self):
        """Вернуть конечное поле цепочки."""
        return self.fields[-1]

    @property
    def path(self):
        """Вернуть OData-путь через связанные поля."""
        return '/'.join(f.odata_name for f in self.fields)

    def startswith(self, value: str) -> FuncExpr:
        """Построить проверку начала строкового поля."""
        return FuncExpr('startswith', self, value)

    def endswith(self, value: str) -> FuncExpr:
        """Построить проверку окончания строкового поля."""
        return FuncExpr('endswith', self, value)

    # NB: не подсвечивает линтер, создана вспомогательная функция
    def contains(self, value: str) -> FuncExpr:
        """Построить проверку вхождения значения в строковое поле."""
        return FuncExpr('contains', self, value)

    # NB: не подсвечивает линтер, создана вспомогательная функция
    def in_(self, values: Iterable[T]) -> InExpr:
        """Построить проверку принадлежности поля коллекции значений."""
        return InExpr(self, values)

    @overload
    def then[RelatedT, U](
        self: FieldRef[ModelT, list[RelatedT]],
        next_ref: FieldRef[RelatedT, U],
    ) -> PathRef[U]: ...

    @overload
    def then[RelatedT, U](
        self: FieldRef[ModelT, RelatedT | None],
        next_ref: FieldRef[RelatedT, U],
    ) -> PathRef[U]: ...

    def then(self, next_ref):
        """Продолжить путь полем целевой модели отношения."""
        terminal = self.field
        if not terminal.is_relation:
            raise AttributeError(f"Cannot traverse scalar field '{terminal.attr_name}'")
        target_model = terminal.get_related_model()
        if next_ref.model is not target_model:
            raise ValueError(
                f'{next_ref.path} belongs to {next_ref.model.__name__}, '
                f'expected {target_model.__name__}'
            )
        return PathRef(next_ref.model, self.fields + next_ref.fields)

    def eq(self, other: object) -> BinExpr:
        """Построить сравнение OData оператором ``eq``."""
        return BinExpr(self, 'eq', other)

    def ne(self, other: object) -> BinExpr:
        """Построить сравнение OData оператором ``ne``."""
        return BinExpr(self, 'ne', other)

    def __eq__(self, other: object) -> BinExpr:  # type: ignore[override]
        return self.eq(other)

    def __ne__(self, other: object) -> BinExpr:  # type: ignore[override]
        return self.ne(other)

    def __gt__(self, other: object) -> BinExpr:
        return BinExpr(self, 'gt', other)

    def __lt__(self, other: object) -> BinExpr:
        return BinExpr(self, 'lt', other)

    def __ge__(self, other: object) -> BinExpr:
        return BinExpr(self, 'ge', other)

    def __le__(self, other: object) -> BinExpr:
        return BinExpr(self, 'le', other)


class PathRef[T](FieldRef[object, T]):
    """Составной путь с типом значения в его текущей конечной точке."""


def like(field: FieldRef, pattern: str):
    """Построить специфичную для 1С функцию сопоставления с шаблоном."""
    return FuncExpr('like', field, pattern)


def contains(field: FieldRef, value: str):
    """Построить функцию проверки вхождения для указанного поля."""
    return FuncExpr('contains', field, value)

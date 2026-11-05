"""Ссылки на поля моделей для путей, сравнений и функций OData."""

from collections.abc import Iterable
from typing import TypeVar

from py1cORM.odata.expressions import BinExpr, FuncExpr, InExpr

T = TypeVar('T')


class FieldRef[T]:
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

    def __getattr__(self, item):
        # --- операции над полем ---
        # if item == 'contains':
        #     return lambda value: FuncExpr('contains', self, value)
        #
        # if item == 'in_':
        #     return lambda values: InExpr(self, values)
        #
        # if item == 'startswith':
        #     return lambda \
        #         value: FuncExpr('startswith', self, value)
        #
        # if item == 'endswith':
        #     return lambda \
        #         value: FuncExpr('endswith', self, value)

        # --- переход по relation ---
        field = self.field

        if not field.is_relation:
            raise AttributeError(f"Cannot traverse scalar field '{field.attr_name}'")

        target_model = field.get_related_model()

        next_field = target_model._fields.get(item)
        if not next_field:
            raise AttributeError(f'{item} not found in {target_model.__name__}')

        return FieldRef(
            target_model,
            self.fields + [next_field],
        )

    def __eq__(self, other):
        return BinExpr(self, 'eq', other)

    def __ne__(self, other):
        return BinExpr(self, 'ne', other)

    def __gt__(self, other):
        return BinExpr(self, 'gt', other)

    def __lt__(self, other):
        return BinExpr(self, 'lt', other)

    def __ge__(self, other):
        return BinExpr(self, 'ge', other)

    def __le__(self, other):
        return BinExpr(self, 'le', other)


def like(field: FieldRef, pattern: str):
    """Построить специфичную для 1С функцию сопоставления с шаблоном."""
    return FuncExpr('like', field, pattern)


def contains(field: FieldRef, value: str):
    """Построить функцию проверки вхождения для указанного поля."""
    return FuncExpr('contains', field, value)

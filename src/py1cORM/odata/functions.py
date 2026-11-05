"""Функциональные помощники для построения выражений OData."""

from py1cORM.odata.expressions import FuncExpr, InExpr
from py1cORM.odata.fields import FieldRef


def contains(field: FieldRef, value: str):
    """Построить проверку вхождения значения в поле."""
    return FuncExpr('contains', field, value)


def in_(field: FieldRef, values):
    """Построить проверку принадлежности поля коллекции значений."""
    return InExpr(field, values)

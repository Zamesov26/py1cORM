"""Выражения для декларативного построения параметра OData ``$filter``."""

from typing import TYPE_CHECKING

from py1cORM.odata.serializers import serialize_value

if TYPE_CHECKING:
    from py1cORM.odata.fields import FieldRef


class Expr:
    """Базовый контракт выражения, сериализуемого в синтаксис OData."""

    def to_odata(self) -> str:
        """Сериализовать выражение в строку OData."""
        raise NotImplementedError


class AndExpr(Expr):
    """Логическое объединение выражений оператором ``and``."""

    def __init__(self, *items):
        self.items = items

    def to_odata(self):
        """Сериализовать дочерние выражения как группу ``and``."""
        return '(' + ' and '.join(i.to_odata() for i in self.items) + ')'


class OrExpr(Expr):
    """Логическое объединение выражений оператором ``or``."""

    def __init__(self, *items):
        self.items = items

    def to_odata(self):
        """Сериализовать дочерние выражения как группу ``or``."""
        return '(' + ' or '.join(i.to_odata() for i in self.items) + ')'


class BinExpr(Expr):
    """Бинарное сравнение поля с сериализуемым значением."""

    def __init__(self, left: 'FieldRef', op: str, right):
        self.left, self.op, self.right = left, op, right

    def to_odata(self):
        """Сериализовать бинарное сравнение."""
        right = serialize_value(self.right, field=self.left.field)
        return f'{self.left.path} {self.op} {right}'


class FuncExpr(Expr):
    """Вызов функции OData над полем и значением."""

    def __init__(self, func_name, field_ref, value):
        self.func_name = func_name
        self.field_ref = field_ref
        self.value = value

    def to_odata(self):
        """Сериализовать вызов функции OData."""
        serialized_value = serialize_value(
            self.value,
            field=self.field_ref.field,
        )

        return f'{self.func_name}({self.field_ref.path}, {serialized_value})'


class RawExpr:
    """Готовое выражение OData без дополнительного преобразования."""

    def __init__(self, raw):
        self.raw = raw

    def to_odata(self):
        """Вернуть исходную строку выражения."""
        return self.raw


class InExpr:
    """Проверка принадлежности значения поля коллекции."""

    def __init__(self, field_ref, values):
        self.field_ref = field_ref
        self.values = values

    def to_odata(self):
        """Сериализовать выражение с оператором ``in``."""
        serialized = serialize_value(
            self.values,
            field=self.field_ref.field,
        )
        return f'{self.field_ref.path} in {serialized}'


def AND(*items):
    """Объединить выражения логическим оператором ``and``."""
    return AndExpr(*items)


def OR(*items):
    """Объединить выражения логическим оператором ``or``."""
    return OrExpr(*items)

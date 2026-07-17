from py1cORM.odata.expressions import FuncExpr, InExpr
from py1cORM.odata.fields import FieldRef


def contains(field: FieldRef, value: str):
    return FuncExpr('contains', field, value)


def in_(field: FieldRef, values):
    return InExpr(field, values)

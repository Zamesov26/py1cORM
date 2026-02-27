from typing import TYPE_CHECKING

from PyOData1C.odata.serializers import serialize_value

if TYPE_CHECKING:
    from odata.fields import FieldRef


class Expr:
    def to_odata(self) -> str:
        raise NotImplementedError


class AndExpr(Expr):
    def __init__(self, *items):
        self.items = items
    
    def to_odata(self):
        return "(" + " and ".join(i.to_odata() for i in self.items) + ")"


class OrExpr(Expr):
    def __init__(self, *items):
        self.items = items
    
    def to_odata(self):
        return "(" + " or ".join(i.to_odata() for i in self.items) + ")"


class BinExpr(Expr):
    def __init__(self, left: "FieldRef", op: str, right):
        self.left, self.op, self.right = left, op, right
    
    def to_odata(self) -> str:
        return f"{self.left.path} {self.op} {serialize_value(self.right)}"

class FuncExpr:
    def __init__(self, func_name, field_ref, value):
        self.func_name = func_name
        self.field_ref = field_ref
        self.value = value
    
    def to_odata(self):
        return f"{self.func_name}({self.field_ref.path}, {serialize_value(self.value)})"


class RawExpr:
    def __init__(self, raw):
        self.raw = raw
    
    def to_odata(self):
        return self.raw

def AND(*items):
    return AndExpr(*items)

def OR(*items):
    return OrExpr(*items)
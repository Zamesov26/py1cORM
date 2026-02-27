from PyOData1C.odata.query import kwargs_to_expr
from tests.models import Product


def test_eq_lookup():
    expr = kwargs_to_expr(Product, {"name": "Test"})
    assert expr.to_odata() == "Description eq 'Test'"


def test_contains_lookup():
    expr = kwargs_to_expr(Product, {"name__contains": "abc"})
    assert expr.to_odata() == "contains(Description, 'abc')"


def test_isnull_true():
    expr = kwargs_to_expr(Product, {"name__isnull": True})
    assert expr.to_odata() == "Description eq null"


def test_multiple_conditions():
    expr = kwargs_to_expr(Product, {
        "name__contains": "abc",
        "category__isnull": False,
    })
    odata = expr.to_odata()
    assert "and" in odata
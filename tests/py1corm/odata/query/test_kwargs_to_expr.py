import pytest
from tests.models import Product

from py1cORM.odata.query import kwargs_to_expr


def test_builds_equality_expression_when_lookup_is_omitted():
    expr = kwargs_to_expr(Product, {'name': 'Test'})
    assert expr.to_odata() == "Description eq 'Test'"


def test_builds_contains_expression_when_lookup_is_contains():
    expr = kwargs_to_expr(Product, {'name__contains': 'abc'})
    assert expr.to_odata() == "contains(Description, 'abc')"


def test_builds_null_expression_when_isnull_is_true():
    expr = kwargs_to_expr(Product, {'name__isnull': True})
    assert expr.to_odata() == 'Description eq null'


def test_combines_expressions_when_multiple_conditions_are_given():
    expr = kwargs_to_expr(
        Product,
        {
            'name__contains': 'abc',
            'category__isnull': False,
        },
    )
    odata = expr.to_odata()
    assert 'and' in odata


def test_rejects_expression_when_field_is_unknown():
    with pytest.raises(ValueError, match='Unknown field'):
        kwargs_to_expr(Product, {'unknown': 'value'})


def test_rejects_expression_when_lookup_is_unsupported():
    with pytest.raises(ValueError, match='Unsupported lookup'):
        kwargs_to_expr(Product, {'name__regex': 'value'})

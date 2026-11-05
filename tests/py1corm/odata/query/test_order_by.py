import pytest
from tests.models import Category, Product

from py1cORM.odata.query import QuerySet


def test_uses_field_path_when_direction_is_omitted():
    qs = QuerySet(None, Product).order_by('name')

    assert qs.spec.orderby == ['Description']


def test_uses_direction_when_order_tuple_is_valid():
    qs = QuerySet(None, Product).order_by(
        ('name', 'asc'), (Product.category.then(Category.name), 'desc')
    )

    assert qs.spec.orderby == ['Description asc', 'Category/Name desc']


def test_rejects_ordering_when_direction_is_unknown():
    with pytest.raises(ValueError, match='Order direction'):
        QuerySet(None, Product).order_by(('name', 'sideways'))


def test_rejects_ordering_when_tuple_has_wrong_length():
    with pytest.raises(ValueError, match='Order tuple'):
        QuerySet(None, Product).order_by(('name', 'asc', 'extra'))

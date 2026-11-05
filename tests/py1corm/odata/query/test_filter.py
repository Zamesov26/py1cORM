import pytest
from tests.models import Category, Parent, Product

from py1cORM.odata.query import QuerySet


class DummyClient:
    def get_collection(self, entity, spec):
        return []


def test_stores_serialized_filter_when_expression_is_given():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter(Product.category.then(Category.parent).then(Parent.name) == 'X')
    qs._finalize_defaults()

    assert qs.spec.filter == "Category/Parent/Name eq 'X'"


def test_stores_filter_unchanged_when_raw_string_is_given():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter("Category/Parent/Name eq 'X'")
    qs._finalize_defaults()

    assert qs.spec.filter == "Category/Parent/Name eq 'X'"


def test_combines_conditions_when_multiple_expressions_are_given():
    qs = QuerySet(DummyClient(), Product).filter(
        Product.name == 'Cup',
        Product.category.then(Category.name) == 'Tableware',
    )

    assert qs.spec.filter == ("(Description eq 'Cup' and Category/Name eq 'Tableware')")


def test_combines_conditions_when_expression_and_raw_string_are_given():
    qs = QuerySet(DummyClient(), Product).filter(
        Product.name == 'Cup', 'Category_Key ne null'
    )

    assert qs.spec.filter == "(Description eq 'Cup' and Category_Key ne null)"


def test_preserves_source_query_when_raw_filter_is_added():
    source = QuerySet(DummyClient(), Product)

    filtered = source.filter("Description eq 'Cup'")

    assert source.spec.filter is None
    assert filtered.spec.filter == "Description eq 'Cup'"


def test_rejects_filter_when_condition_type_is_unsupported():
    with pytest.raises(TypeError, match='Unsupported filter argument'):
        QuerySet(DummyClient(), Product).filter(object())

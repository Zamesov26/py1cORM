from tests.models import Product

from py1cORM.odata.query import QuerySet


class DummyClient:
    def get_collection(self, entity, spec):
        return []


def test_stores_serialized_filter_when_expression_is_given():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter(Product.category.parent.name == 'X')
    qs._finalize_defaults()

    assert qs.spec.filter == "Category/Parent/Name eq 'X'"


def test_stores_filter_unchanged_when_raw_string_is_given():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter("Category/Parent/Name eq 'X'")
    qs._finalize_defaults()

    assert qs.spec.filter == "Category/Parent/Name eq 'X'"

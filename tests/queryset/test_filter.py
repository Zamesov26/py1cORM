from py1cORM.odata.query import QuerySet
from tests.models import Product


class DummyClient:
    def get_collection(self, entity, spec):
        return []


def test_filter_expr():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter(Product.category.parent.name=="X")
    qs._finalize_defaults()
    
    assert qs.spec.filter == "Category/Parent/Name eq 'X'"
    

def test_filter_raw_string():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.filter("Category/Parent/Name eq 'X'")
    qs._finalize_defaults()

    assert qs.spec.filter == "Category/Parent/Name eq 'X'"

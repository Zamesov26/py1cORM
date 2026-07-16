from py1cORM.odata.query import QuerySet
from tests.models import Product


class DummyClient:
    def get_collection(self, entity, spec):
        return []


def test_without_select_fields():
    qs = QuerySet(DummyClient(), Product)
    qs._finalize_defaults()

    assert qs.spec.select is None


def test_explicit_select_override():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.select('name')
    qs._finalize_defaults()

    assert qs.spec.select == ['Description']

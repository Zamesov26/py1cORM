from tests.models import Product

from py1cORM.odata.query import QuerySet


class DummyClient:
    def get_collection(self, entity, spec):
        return []


def test_leaves_select_unset_when_fields_are_not_given():
    qs = QuerySet(DummyClient(), Product)
    qs._finalize_defaults()

    assert qs.spec.select is None


def test_uses_explicit_fields_when_select_is_called():
    qs = QuerySet(DummyClient(), Product)
    qs = qs.select('name')
    qs._finalize_defaults()

    assert qs.spec.select == ['Description']

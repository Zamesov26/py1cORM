from tests.models import Product

from py1cORM.odata.query import QuerySet


def test_sets_top_and_skip_when_pagination_is_configured():
    qs = QuerySet(None, Product).paginate(top=10, skip=20)

    assert qs.spec.top == 10
    assert qs.spec.skip == 20


def test_preserves_source_query_when_pagination_is_configured():
    source = QuerySet(None, Product)

    source.paginate(top=10, skip=20)

    assert source.spec.top is None
    assert source.spec.skip is None

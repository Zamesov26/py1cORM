from tests.models import Product

from py1cORM.odata.utils import field_to_path


def test_returns_full_path_when_multiple_relations_are_traversed():
    assert field_to_path(Product, 'category__parent__name') == 'Category/Parent/Name'

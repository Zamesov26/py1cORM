from py1cORM.odata.utils import field_to_path
from tests.models import Product


def test_deep_foreign_path():
    assert field_to_path(Product, "category__parent__name") == "Category/Parent/Name"
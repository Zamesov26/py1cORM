from PyOData1C.odata.utils import field_to_path
from tests.models import Product


def test_scalar_path():
    assert field_to_path(Product, "name") == "Description"


def test_foreign_path():
    assert field_to_path(Product, "category__name") == "Category/Name"


def test_fieldref_path():
    assert field_to_path(Product, Product.name) == "Description"
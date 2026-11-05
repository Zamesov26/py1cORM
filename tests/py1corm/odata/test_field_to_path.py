from tests.models import Product

from py1cORM.odata.utils import field_to_path


def test_returns_alias_when_field_is_scalar():
    assert field_to_path(Product, 'name') == 'Description'


def test_returns_slash_path_when_field_traverses_relation():
    assert field_to_path(Product, 'category__name') == 'Category/Name'


def test_returns_existing_path_when_field_reference_is_given():
    assert field_to_path(Product, Product.name) == 'Description'

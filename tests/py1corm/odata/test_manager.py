from unittest.mock import Mock

from tests.models import Product

from py1cORM.odata.manager import Manager


def test_loads_entities_when_all_is_called():
    client = Mock()
    client.get_collection.return_value = [{'Description': 'Cup'}]

    items = Manager(client, Product).all()

    assert [item.name for item in items] == ['Cup']


def test_returns_filtered_query_when_filter_is_called():
    query = Manager(Mock(), Product).filter(Product.name == 'Cup')

    assert query.spec.filter == "Description eq 'Cup'"


def test_returns_selected_query_when_select_is_called():
    query = Manager(Mock(), Product).select(Product.name)

    assert query.spec.select == ['Description']


def test_returns_expanded_query_when_expand_is_called():
    query = Manager(Mock(), Product).expand(Product.category)

    assert query.spec.expand == ['Category']


def test_delegates_lookup_when_get_is_called():
    client = Mock()
    client.get_collection.return_value = [{'Description': 'Cup'}]

    item = Manager(client, Product).get(name='Cup')

    assert item.name == 'Cup'

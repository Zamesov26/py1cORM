from unittest.mock import Mock

import pytest
from tests.models import Product

from py1cORM.odata.query import QuerySet


def test_returns_entity_when_exactly_one_item_matches():
    client = Mock()
    client.get_collection.return_value = [{'Description': 'Cup'}]

    item = QuerySet(client, Product).get(name='Cup')

    assert item.name == 'Cup'
    spec = client.get_collection.call_args.args[1]
    assert spec.filter == "Description eq 'Cup'"
    assert spec.top == 2


def test_raises_not_found_when_collection_is_empty():
    client = Mock()
    client.get_collection.return_value = []

    with pytest.raises(LookupError, match='Not found'):
        QuerySet(client, Product).get(name='Unknown')


def test_raises_multiple_objects_when_more_than_one_item_matches():
    client = Mock()
    client.get_collection.return_value = [
        {'Description': 'Cup'},
        {'Description': 'Cup'},
    ]

    with pytest.raises(LookupError, match='Multiple objects'):
        QuerySet(client, Product).get(name='Cup')

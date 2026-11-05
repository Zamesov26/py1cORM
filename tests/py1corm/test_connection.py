from unittest.mock import Mock, patch

import pytest
import requests

from py1cORM.connection import ODataConnection
from py1cORM.odata.query import QuerySpec


def make_connection(**kwargs) -> ODataConnection:
    return ODataConnection(
        host='https://example.test/',
        database='base',
        username='user',
        password='password',
        **kwargs,
    )


def test_builds_encoded_request_when_query_spec_contains_all_parameters():
    response = Mock()
    response.json.return_value = {'value': [{'Ref_Key': 'id'}]}
    spec = QuerySpec(
        select=['Ref_Key', 'Description'],
        expand=['Category'],
        filter="Description eq 'Стакан'",
        orderby=['Description asc'],
        top=10,
        skip=20,
    )

    with patch('py1cORM.connection.requests.get', return_value=response) as get:
        result = make_connection().get_collection('Catalog_Items', spec)

    assert result == [{'Ref_Key': 'id'}]
    get.assert_called_once()
    url = get.call_args.args[0]
    assert url == (
        'https://example.test/base/odata/standard.odata/Catalog_Items?'
        '%24select=Ref_Key%2CDescription&%24expand=Category&'
        '%24filter=Description%20eq%20%27%D0%A1%D1%82%D0%B0%D0%BA%D0%B0%D0%BD%27&'
        '%24orderby=Description%20asc&%24top=10&%24skip=20&%24format=json'
    )
    assert get.call_args.kwargs['auth'].username == 'user'
    assert get.call_args.kwargs['auth'].password == 'password'
    assert get.call_args.kwargs['timeout'] == (10, 121)
    response.raise_for_status.assert_called_once_with()


def test_uses_configured_timeout_when_values_are_overridden():
    response = Mock()
    response.json.return_value = {'value': []}

    with patch('py1cORM.connection.requests.get', return_value=response) as get:
        make_connection(connection_timeout=2, read_timeout=30).get_collection(
            'Catalog_Items', QuerySpec()
        )

    assert get.call_args.kwargs['timeout'] == (2, 30)


def test_returns_empty_collection_when_value_is_absent_from_response():
    response = Mock()
    response.json.return_value = {}

    with patch('py1cORM.connection.requests.get', return_value=response):
        result = make_connection().get_collection('Catalog_Items', QuerySpec())

    assert result == []


def test_propagates_http_error_when_response_status_is_unsuccessful():
    response = Mock()
    response.raise_for_status.side_effect = requests.HTTPError('server error')

    with (
        patch('py1cORM.connection.requests.get', return_value=response),
        pytest.raises(requests.HTTPError, match='server error'),
    ):
        make_connection().get_collection('Catalog_Items', QuerySpec())

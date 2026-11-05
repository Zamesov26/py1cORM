from unittest.mock import Mock, patch

import pytest
import requests

from py1cORM.exceptions import ClientConnectionError
from py1cORM.http_client import Connection, Request


def make_connection() -> Connection:
    return Connection(
        host='example.test',
        protocol='https',
        authentication=Mock(),
        connection_timeout=2,
        read_timeout=30,
    )


def test_encodes_query_parameters_when_building_url():
    url = make_connection().get_url('odata/Items', {'$filter': "Description eq 'Cup'"})

    assert url == (
        'https://example.test/odata/Items?%24filter=Description%20eq%20%27Cup%27'
    )


def test_reuses_and_closes_session_when_context_manager_is_used():
    session = Mock(spec=requests.Session)
    connection = make_connection()

    with (
        patch.object(connection, '_create_session', return_value=session),
        connection as active,
    ):
        assert active is connection
        assert active._session is session

    session.close.assert_called_once_with()


def test_sends_request_with_timeout_when_temporary_session_is_used():
    response = Mock(spec=requests.Response)
    session = Mock(spec=requests.Session)
    session.prepare_request.return_value = Mock()
    session.send.return_value = response
    connection = make_connection()

    with patch.object(connection, '_create_session', return_value=session):
        result = connection.send_request(
            Request(method='GET', relative_url='odata/Items')
        )

    assert result is response
    session.send.assert_called_once_with(
        session.prepare_request.return_value, timeout=(2, 30)
    )
    session.close.assert_called_once_with()


@pytest.mark.parametrize(
    'error', [requests.ConnectionError('unavailable'), requests.Timeout('timeout')]
)
def test_raises_client_connection_error_when_transport_fails(error):
    session = Mock(spec=requests.Session)
    session.prepare_request.return_value = Mock()
    session.send.side_effect = error
    connection = make_connection()

    with (
        patch.object(connection, '_create_session', return_value=session),
        pytest.raises(ClientConnectionError),
    ):
        connection.send_request(Request(method='GET', relative_url='odata/Items'))

    session.close.assert_called_once_with()

"""Низкоуровневые HTTP-запросы с управлением сессией и тайм-аутами."""

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode

import requests
import requests.auth as auth
import requests.exceptions as r_exceptions

from py1cORM.exceptions import ClientConnectionError


@dataclass
class Request:
    """Описание HTTP-запроса относительно базового адреса подключения."""

    method: str
    relative_url: str
    query_params: dict[str, Any] | None = None
    data: dict[str, Any] | None = None


class Connection:
    """HTTP-подключение с аутентификацией и раздельными тайм-аутами."""

    def __init__(
        self,
        host: str,
        protocol: str,
        authentication: auth.AuthBase,
        connection_timeout: int | float = 10,
        read_timeout: int | float = 121,
    ) -> None:
        self.base_url = f'{protocol}://{host}/'
        self.connection_timeout = connection_timeout
        self.read_timeout = read_timeout
        self.auth = authentication
        self.headers = {
            'Accept': 'application/json',
        }
        self._session: requests.Session | None = None

    def __enter__(self) -> 'Connection':
        self._session = self._create_session()
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.auth = self.auth
        session.headers.update(self.headers)
        return session

    def get_url(
        self, relative_url: str, query_params: dict[str, Any] | None = None
    ) -> str:
        """Собрать абсолютный URL и закодировать query-параметры."""
        url = f'{self.base_url}{relative_url}'
        if query_params:
            url = f'{url}?{urlencode(query_params, quote_via=quote)}'
        return url

    def send_request(self, request: Request) -> requests.Response:
        """Отправить подготовленный запрос и преобразовать сетевые ошибки."""
        session = self._session or self._create_session()
        url = self.get_url(request.relative_url, request.query_params)
        req = requests.Request(method=request.method, url=url, json=request.data)
        prepared = session.prepare_request(req)
        try:
            response: requests.Response = session.send(
                prepared, timeout=(self.connection_timeout, self.read_timeout)
            )
        except (r_exceptions.ConnectionError, r_exceptions.Timeout):
            raise ClientConnectionError from None
        finally:
            if self._session is None:
                session.close()
        return response

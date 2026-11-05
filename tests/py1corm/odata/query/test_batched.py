from unittest.mock import call, patch

import pytest

from py1cORM.odata.query import QuerySet


class DummyClient:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def get_collection(self, entity_name, spec):
        # сохраняем вызовы для проверки
        self.calls.append((spec.top, spec.skip))

        top = spec.top or len(self.data)
        skip = spec.skip or 0

        return self.data[skip : skip + top]


class DummyModel:
    class Meta:
        entity_name = 'test'

    _fields = {}

    @classmethod
    def from_raw(cls, raw):
        return raw


def test_returns_all_items_when_collection_spans_multiple_batches():
    """Проверить отсутствие потерь данных на границах нескольких страниц."""
    data = list(range(250))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.batched(batch_size=100))

    # ---------------------------
    # проверяем батчи
    # ---------------------------
    assert len(result) == 3
    assert [len(batch) for batch in result] == [100, 100, 50]

    # ---------------------------
    # проверяем данные
    # ---------------------------
    flat = [item for batch in result for item in batch]
    assert flat == data


def test_requests_sequential_offsets_when_iterating_batches():
    """Проверить смещения страниц и завершающий запрос за пустой страницей."""
    data = list(range(250))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    list(qs.batched(batch_size=100))

    assert client.calls == [
        (100, 0),
        (100, 100),
        (100, 200),
        (100, 300),  # последний пустой батч
    ]


def test_stops_iteration_when_server_returns_empty_batch():
    data = list(range(50))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.batched(batch_size=100))

    # ---------------------------
    # один батч
    # ---------------------------
    assert len(result) == 1
    assert len(result[0]) == 50

    # ---------------------------
    # данные не потерялись
    # ---------------------------
    flat = [item for batch in result for item in batch]
    assert flat == data


def test_returns_complete_batches_when_size_is_exact_multiple():
    """Не возвращать лишнюю страницу, когда объём кратен размеру пакета."""
    data = list(range(200))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.batched(batch_size=100))

    # ---------------------------
    # ровно 2 батча
    # ---------------------------
    assert len(result) == 2
    assert [len(batch) for batch in result] == [100, 100]

    # ---------------------------
    # данные не потерялись
    # ---------------------------
    flat = [item for batch in result for item in batch]
    assert flat == data


def test_waits_between_requests_when_delay_is_positive():
    """Делать паузу только между запросами, включая запрос завершения."""
    client = DummyClient(list(range(3)))
    qs = QuerySet(client, DummyModel)

    with patch('py1cORM.odata.query.sleep') as sleep:
        result = list(qs.batched(batch_size=2, delay=0.5))

    assert result == [[0, 1], [2]]
    assert sleep.call_args_list == [call(0.5), call(0.5)]


def test_rejects_iteration_when_delay_is_negative():
    qs = QuerySet(DummyClient([]), DummyModel)

    with pytest.raises(ValueError, match='Delay cannot be negative'):
        list(qs.batched(delay=-1))


@pytest.mark.parametrize('batch_size', [0, -1])
def test_rejects_iteration_when_batch_size_is_not_positive(batch_size):
    qs = QuerySet(DummyClient([]), DummyModel)

    with pytest.raises(ValueError, match='Batch size must be positive'):
        list(qs.batched(batch_size=batch_size))

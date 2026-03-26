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


def test_iterator_returns_all_items_in_batches():
    data = list(range(250))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.iterator(batch_size=100))

    assert result == data


def test_iterator_calls_with_correct_pagination():
    data = list(range(250))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    list(qs.iterator(batch_size=100))

    assert client.calls == [
        (100, 0),
        (100, 100),
        (100, 200),
        (100, 300),  # последний пустой батч
    ]


def test_iterator_stops_on_empty_batch():
    data = list(range(50))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.iterator(batch_size=100))

    assert result == data
    assert client.calls == [
        (100, 0),
        (100, 100),
    ]


def test_iterator_with_exact_multiple_of_batch():
    data = list(range(200))

    client = DummyClient(data)
    qs = QuerySet(client, DummyModel)

    result = list(qs.iterator(batch_size=100))

    assert result == data
    assert client.calls == [
        (100, 0),
        (100, 100),
        (100, 200),  # пустой батч обязателен
    ]

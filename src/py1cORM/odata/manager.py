"""Фасад создания запросов для закреплённых клиента и модели."""

from py1cORM.odata.query import QuerySet


class Manager:
    """Предоставить операции QuerySet для конкретной модели и клиента."""

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def all(self):
        """Загрузить все доступные сущности модели."""
        return QuerySet(self.client, self.model).all()

    def filter(self, expr):
        """Создать запрос с указанным выражением фильтрации."""
        return QuerySet(self.client, self.model).filter(expr)

    def select(self, *fields):
        """Создать запрос с явным набором загружаемых полей."""
        return QuerySet(self.client, self.model).select(*fields)

    def expand(self, *fields):
        """Создать запрос с раскрытием связанных полей."""
        return QuerySet(self.client, self.model).expand(*fields)

    def get(self, **kwargs):
        """Получить единственную сущность по условиям полей."""
        return QuerySet(self.client, self.model).get(**kwargs)

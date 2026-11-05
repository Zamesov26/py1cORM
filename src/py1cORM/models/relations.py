"""Объекты времени выполнения для связей между сущностями OData."""


class FK:
    """Прокси внешнего ключа с GUID и опционально загруженной сущностью."""

    def __init__(self, key=None, entity=None):
        self._id = key
        self._entity = entity

    def is_loaded(self):
        """Проверить, загружена ли связанная сущность."""
        return self._entity is not None

    def has_key(self):
        """Проверить, содержит ли связь GUID связанной сущности."""
        return self._id is not None

    @property
    def id(self):
        """Вернуть GUID связанной сущности или ``None``."""
        return self._id

    def __getattr__(self, item):
        if self._entity is None:
            raise AttributeError(
                f'FK not loaded (key={self._id}). Use expand() to load related entity.'
            )
        return getattr(self._entity, item)

    def __repr__(self):
        if self._entity:
            return f'<FK loaded {self._entity}>'
        return f'<FK key={self._id}>'

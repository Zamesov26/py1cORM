class FK:
    def __init__(self, key=None, entity=None):
        self._id = key
        self._entity = entity

    def is_loaded(self):
        return self._entity is not None

    def has_key(self):
        return self._id is not None

    @property
    def id(self):
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

class FK:
    def __init__(self, key=None, entity=None):
        self._id = key
        self._entity = entity

    def is_loaded(self):
        return self._entity is not None

    def __repr__(self):
        if self._entity:
            return f'<FK loaded {self._entity}>'
        return f'<FK key={self._id}>'

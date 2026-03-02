class FK:
    def __init__(self, key=None, entity=None):
        self.key = key
        self.entity = entity

    def is_loaded(self):
        return self.entity is not None

    def __repr__(self):
        if self.entity:
            return f'<FK loaded {self.entity}>'
        return f'<FK key={self.key}>'

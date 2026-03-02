class Field:
    def __init__(self, *, alias: str | None = None):
        self.alias = alias
        self.name = None
        self.annotation = None

    def bind(self, model, name, annotation):
        self.name = name
        self.annotation = annotation
        if self.alias is None:
            self.alias = name


class ForeignKey:
    def __init__(self, *, model, alias: str, key_field: str):
        self.model = model
        self.alias = alias
        self.key_field = key_field

        self.name = None
        self.annotation = None

    def bind(self, model_cls, field_name, annotation):
        self.name = field_name
        self.annotation = annotation

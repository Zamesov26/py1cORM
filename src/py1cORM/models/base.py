from .fields import Field


class ODataModelMeta(type):
    def __new__(cls, name, bases, namespace):
        annotations = namespace.get('__annotations__', {})
        declared = {}

        for attr_name, attr_value in list(namespace.items()):
            if isinstance(attr_value, Field):
                declared[attr_name] = attr_value
                del namespace[attr_name]  # <-- ВАЖНО

        new_cls = super().__new__(cls, name, bases, namespace)

        new_cls._fields = {}
        new_cls._alias_map = {}

        for field_name, field in declared.items():
            annotation = annotations.get(field_name)
            field.bind(new_cls, field_name, annotation)

            new_cls._fields[field_name] = field
            new_cls._alias_map[field.alias] = field_name

            if getattr(field, 'is_foreign_key', False):
                new_cls._alias_map[field.key_field] = field_name

        return new_cls

    def __getattr__(cls, item):
        fields = getattr(cls, '_fields', {})

        if item in fields:
            return fields[item].ref()

        raise AttributeError(item)


class ODataModel(metaclass=ODataModelMeta):
    @classmethod
    def from_raw(cls, raw: dict):
        from py1cORM.parser.entity import Entity

        return Entity(cls, raw)

    @classmethod
    def using(cls, connection):
        from py1cORM.odata.query import QuerySet

        return QuerySet(connection, cls)

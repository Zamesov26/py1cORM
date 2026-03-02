from .fields import Field, ForeignKey


class ODataModelMeta(type):
    def __new__(cls, name, bases, namespace):
        annotations = namespace.get('__annotations__', {})
        declared = {}

        # собираем только Field
        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, (Field, ForeignKey)):
                declared[attr_name] = attr_value

        new_cls = super().__new__(cls, name, bases, namespace)

        new_cls._fields = {}
        new_cls._alias_map = {}

        for field_name, field in declared.items():
            annotation = annotations.get(field_name)
            field.bind(new_cls, field_name, annotation)

            new_cls._fields[field_name] = field
            if isinstance(field, ForeignKey):
                new_cls._alias_map[field.key_field] = field_name
            new_cls._alias_map[field.alias] = field_name

        return new_cls


class ODataModel(metaclass=ODataModelMeta):
    @classmethod
    def from_raw(cls, raw: dict):
        from py1cORM.parser.entity import Entity

        return Entity(cls, raw)

"""Базовая модель OData и метакласс сбора декларативных полей."""

from typing import Any, ClassVar

from .fields import Field, ForeignKey


class ODataModelMeta(type):
    """Метакласс, связывающий объявленные поля с моделью OData."""

    _fields: dict[str, Field[Any]]
    _alias_map: dict[str | None, str]

    def __new__(cls, name, bases, namespace):
        """Создать класс модели и собрать объявленные в нём поля."""
        annotations = namespace.get('__annotations__', {})
        declared = {}

        for attr_name, attr_value in list(namespace.items()):
            if isinstance(attr_value, Field):
                declared[attr_name] = attr_value
                del namespace[attr_name]  # <-- ВАЖНО

        new_cls = super().__new__(cls, name, bases, namespace)

        fields = {}
        alias_map = {}

        for field_name, field in declared.items():
            annotation = annotations.get(field_name)
            field.bind(new_cls, field_name, annotation)

            fields[field_name] = field
            alias_map[field.alias] = field_name

            if isinstance(field, ForeignKey):
                alias_map[field.key_field] = field_name

        new_cls._fields = fields
        new_cls._alias_map = alias_map

        return new_cls

    def __getattr__(cls, item):
        fields = getattr(cls, '_fields', {})

        if item in fields:
            return fields[item].ref()

        raise AttributeError(item)


class ODataModel(metaclass=ODataModelMeta):
    """Базовый класс декларативных моделей сущностей OData."""

    Meta: ClassVar[Any]
    _fields: ClassVar[dict[str, Field[Any]]]
    _alias_map: ClassVar[dict[str | None, str]]

    @classmethod
    def from_raw(cls, raw: dict):
        """Создать сущность модели из словаря ответа OData."""
        from py1cORM.parser.entity import Entity

        return Entity(cls, raw)

    @classmethod
    def using(cls, connection):
        """Создать набор запросов модели для указанного подключения."""
        from py1cORM.odata.query import QuerySet

        return QuerySet(connection, cls)

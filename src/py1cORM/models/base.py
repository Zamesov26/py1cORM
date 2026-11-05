"""Базовая модель OData и метакласс сбора декларативных полей."""

from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Self,
    get_args,
    get_origin,
    get_type_hints,
)

from py1cORM.models.fields import Field, Mapped, Relationship
from py1cORM.parser.sentinels import NotLoaded

if TYPE_CHECKING:
    from py1cORM.connection import ODataConnection
    from py1cORM.odata.query import QuerySet


class ODataModelMeta(type):
    """Метакласс, связывающий дескрипторы полей с моделью OData."""

    _fields: dict[str, Field[Any]]
    _alias_map: dict[str | None, str]

    def __new__(cls, name, bases, namespace):
        """Создать класс модели и собрать объявленные в нём поля."""
        annotations = namespace.get('__annotations__', {})
        new_cls = super().__new__(cls, name, bases, namespace)
        if any(isinstance(value, str) for value in annotations.values()):
            module_globals = vars(sys.modules[new_cls.__module__])
            local_names = {**namespace, name: new_cls}
            annotation_resolver = type(
                f'_{name}AnnotationResolver',
                (),
                {
                    '__annotations__': annotations,
                    '__module__': new_cls.__module__,
                },
            )
            try:
                annotations = get_type_hints(
                    annotation_resolver,
                    globalns=module_globals,
                    localns=local_names,
                )
            except NameError as exc:
                raise TypeError(
                    f"Cannot resolve annotations for OData model '{name}': {exc}"
                ) from exc
        fields = {
            key: value
            for base in bases
            for key, value in getattr(base, '_fields', {}).items()
        }
        alias_map = {
            key: value
            for base in bases
            for key, value in getattr(base, '_alias_map', {}).items()
        }

        for field_name, field in namespace.items():
            if not isinstance(field, Field):
                continue
            annotation = annotations.get(field_name)
            if get_origin(annotation) is not Mapped:
                raise TypeError(
                    f"Field '{name}.{field_name}' must be annotated as Mapped[T]"
                )
            value_type = get_args(annotation)[0]
            field.bind(new_cls, field_name, value_type)
            assert field.alias is not None
            fields[field_name] = field
            alias_map[field.alias] = field_name

        new_cls._fields = fields
        new_cls._alias_map = alias_map
        return new_cls


class ODataModel(metaclass=ODataModelMeta):
    """Базовый класс типизированных сущностей OData."""

    Meta: ClassVar[Any]
    _fields: ClassVar[dict[str, Field[Any]]]
    _alias_map: ClassVar[dict[str | None, str]]
    _extra: dict[str, Any]
    _loaded_fields: set[str]

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any]) -> Self:
        """Создать экземпляр модели из словаря ответа OData."""
        from py1cORM.parser.convert import convert

        instance = cls.__new__(cls)
        instance._extra = {}
        instance._loaded_fields = set()

        for field_name, field in cls._fields.items():
            assert field.alias is not None
            if isinstance(field, Relationship):
                if field.alias not in raw:
                    setattr(instance, field_name, NotLoaded)
                    continue
                related_raw = raw[field.alias]
                entity_value = (
                    field.related_model.from_raw(related_raw)
                    if isinstance(related_raw, dict)
                    else None
                )
                setattr(instance, field_name, entity_value)
                instance._loaded_fields.add(field_name)
                continue

            if field.alias in raw:
                setattr(
                    instance, field_name, convert(raw[field.alias], field.annotation)
                )
                instance._loaded_fields.add(field_name)
            else:
                setattr(instance, field_name, NotLoaded)

        instance._extra = {
            key: value for key, value in raw.items() if key not in cls._alias_map
        }
        return instance

    @classmethod
    def using(cls, connection: ODataConnection) -> QuerySet[Self]:
        """Создать набор запросов модели для указанного подключения."""
        from py1cORM.odata.query import QuerySet

        return QuerySet(connection, cls)

    def extra(self) -> dict[str, Any]:
        """Вернуть поля ответа, которые не объявлены в модели."""
        return dict(self._extra)

    def is_loaded(self, field_name: str) -> bool:
        """Проверить, было ли поле загружено из ответа OData."""
        return field_name in self._loaded_fields

    @staticmethod
    def _safe_repr(value: object) -> str:
        try:
            return repr(value)
        except Exception as exc:
            return f'<repr failed: {type(exc).__name__}: {exc}>'

    def __repr__(self) -> str:
        model_name = type(self).__name__
        if '__str__' in type(self).__dict__:
            try:
                return f'<{model_name} {self}>'
            except Exception:
                pass
        repr_fields = getattr(getattr(type(self), 'Meta', None), 'repr_fields', None)
        parts = []
        for field_name in repr_fields or self._loaded_fields:
            if not self.is_loaded(field_name):
                continue
            try:
                parts.append(
                    f'{field_name}={self._safe_repr(getattr(self, field_name))}'
                )
            except Exception:
                continue
        return f'<{model_name} {", ".join(parts)}>'
